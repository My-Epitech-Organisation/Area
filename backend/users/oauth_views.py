##
## EPITECH PROJECT, 2025
## Area
## File description:
## oauth_views
##

"""API views for OAuth2 authentication flow."""

import logging
from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from .models import ServiceToken
from .oauth import OAuthManager
from .oauth.exceptions import InvalidProviderError, OAuthError, OAuthStateError
from .oauth_serializers import (
    OAuthCallbackSerializer,
    OAuthInitiateResponseSerializer,
    ServiceConnectionListSerializer,
    ServiceDisconnectSerializer,
    ServiceTokenSerializer,
)

logger = logging.getLogger(__name__)


class OAuthInitiateView(APIView):
    """
    Initiate OAuth2 authorization flow.

    GET /auth/oauth/{provider}/

    Returns the authorization URL to redirect the user to the OAuth2 provider.
    The user will authenticate and authorize access, then be redirected back
    to the callback URL.

    Path Parameters:
        provider: OAuth2 provider name (google, github, etc.)

    Returns:
        - redirect_url: URL to redirect user to
        - state: CSRF protection token
        - provider: Provider name
        - expires_in: State validity duration in seconds
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OAuthInitiateResponseSerializer

    def get(self, request, provider: str):
        """Generate OAuth2 authorization URL."""
        try:
            # Validate provider exists
            if provider not in settings.OAUTH2_PROVIDERS:
                return Response(
                    {
                        "error": "invalid_provider",
                        "message": f"Provider '{provider}' is not supported",
                        "available_providers": list(settings.OAUTH2_PROVIDERS.keys()),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if provider is properly configured
            if not OAuthManager.is_provider_available(provider):
                return Response(
                    {
                        "error": "provider_not_configured",
                        "message": f"Provider '{provider}' is not properly configured",
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # Generate CSRF state token
            state = OAuthManager.generate_state(
                user_id=str(request.user.id), provider=provider
            )

            # Get OAuth provider and generate authorization URL
            oauth_provider = OAuthManager.get_provider(provider)
            redirect_url = oauth_provider.get_authorization_url(state)

            # Prepare response
            response_data = {
                "redirect_url": redirect_url,
                "state": state,
                "provider": provider,
                "expires_in": getattr(settings, "OAUTH2_STATE_EXPIRY", 600),
            }

            serializer = OAuthInitiateResponseSerializer(response_data)

            logger.info(
                f"User {request.user.email} initiated OAuth2 flow for {provider}"
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except InvalidProviderError as e:
            logger.error(f"Invalid provider error: {str(e)}")
            return Response(
                {"error": "invalid_provider", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Error initiating OAuth2 flow: {str(e)}", exc_info=True)
            return Response(
                {
                    "error": "internal_error",
                    "message": "Failed to initiate OAuth2 flow",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OAuthCallbackView(APIView):
    """
    Handle OAuth2 authorization callback (Backend-First flow).

    GET /auth/oauth/{provider}/callback/?code=xxx&state=yyy

    This endpoint is called by the OAuth2 provider after user authorization.
    It validates the state token, exchanges the code for an access token,
    stores it in the database, and redirects the user to the frontend
    with the result.

    Flow:
        1. OAuth provider redirects browser here with code & state
        2. Backend validates state and retrieves user_id from cache
        3. Backend exchanges code for access token
        4. Backend stores token in database
        5. Backend redirects to frontend with success/error parameters

    Path Parameters:
        provider: OAuth2 provider name (google, github, etc.)

    Query Parameters:
        code: Authorization code (on success)
        state: CSRF protection token (on success)
        error: Error code (on failure)
        error_description: Error description (on failure)

    Redirects to:
        Frontend callback URL with query parameters:
        - On success: ?success=true&service={provider}&created={true|false}
        - On error: ?error={error_type}&message={error_description}
    """

    permission_classes = [AllowAny]  # OAuth providers redirect without auth header
    serializer_class = OAuthCallbackSerializer

    def get(self, request, provider: str):
        """
        Process OAuth2 callback and redirect to frontend with result.

        This method implements the Backend-First OAuth flow where all token
        handling is done server-side for security.
        """
        # Get frontend URL for redirects
        frontend_url = getattr(
            settings, "FRONTEND_URL", None
        ) or request.build_absolute_uri("/").rstrip("/")
        callback_base = f"{frontend_url}/auth/callback/{provider}"

        # Validate callback parameters
        serializer = OAuthCallbackSerializer(data=request.query_params)
        if not serializer.is_valid():
            logger.error(
                f"Invalid OAuth callback parameters for {provider}: "
                f"{serializer.errors}"
            )
            return self._redirect_with_error(
                callback_base, "invalid_callback", "Invalid callback parameters"
            )

        validated_data = serializer.validated_data

        # Handle OAuth provider error
        if validated_data.get("error"):
            error_msg = validated_data.get("error_description", validated_data["error"])
            logger.warning(f"OAuth2 callback error from {provider}: {error_msg}")
            return self._redirect_with_error(
                callback_base, validated_data["error"], error_msg
            )

        code = validated_data["code"]
        state = validated_data["state"]

        try:
            # Step 1: Validate state and retrieve user
            user = self._validate_state_and_get_user(state, provider)

            # Step 2: Exchange code for access token
            oauth_provider = OAuthManager.get_provider(provider)
            token_data = oauth_provider.exchange_code_for_token(code)

            # Step 3: Calculate token expiration
            expires_at = oauth_provider.calculate_expiry(token_data.get("expires_in"))

            # Step 4: Store or update token in database
            service_token, created = ServiceToken.objects.update_or_create(
                user=user,
                service_name=provider,
                defaults={
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token", ""),
                    "expires_at": expires_at,
                    "token_type": token_data.get("token_type", "Bearer"),
                    "scopes": " ".join(oauth_provider.scopes),  # Store granted scopes
                },
            )

            # Log successful connection
            action = "connected" if created else "reconnected"
            logger.info(
                f"User {user.email} successfully {action} to {provider} "
                f"(expires: {expires_at or 'never'})"
            )

            # Resolve any existing notifications for this service
            from users.models import OAuthNotification

            resolved_count = OAuthNotification.resolve_for_service(user, provider)
            if resolved_count > 0:
                logger.info(
                    f"Resolved {resolved_count} OAuth notifications for "
                    f"{user.email}/{provider}"
                )

            # Step 5: Redirect to frontend with success
            return self._redirect_with_success(
                callback_base, provider, created, expires_at
            )

        except OAuthError as e:
            logger.error(
                f"OAuth error during {provider} callback: {str(e)}", exc_info=True
            )
            return self._redirect_with_error(callback_base, "oauth_error", str(e))

        except Exception as e:
            logger.error(
                f"Unexpected error in {provider} callback: {str(e)}", exc_info=True
            )
            return self._redirect_with_error(
                callback_base, "internal_error", "Failed to complete OAuth flow"
            )

    def _validate_state_and_get_user(self, state: str, provider: str):
        """
        Validate OAuth state token and retrieve associated user.

        Args:
            state: OAuth state token from callback
            provider: OAuth provider name

        Returns:
            User: Django User instance

        Raises:
            OAuthError: If state is invalid or user not found
        """
        from django.contrib.auth import get_user_model
        from django.core.cache import cache

        User = get_user_model()

        # Retrieve state data from cache
        cache_key = OAuthManager._get_state_cache_key(state)
        state_data = cache.get(cache_key)

        if not state_data:
            raise OAuthStateError("OAuth state token is invalid or expired")

        user_id = state_data.get("user_id")
        if not user_id:
            raise OAuthStateError("OAuth state missing user information")

        # Validate state (this also deletes it from cache for one-time use)
        is_valid, error_msg = OAuthManager.validate_state(
            state=state, user_id=str(user_id), provider=provider
        )
        if not is_valid:
            raise OAuthStateError(f"State validation failed: {error_msg}")

        # Retrieve user by UUID
        try:
            user_uuid = UUID(user_id)
            user = User.objects.get(id=user_uuid)
            return user
        except (ValueError, TypeError) as e:
            raise OAuthStateError(f"Invalid user identifier in state: {e}") from e
        except User.DoesNotExist as e:
            raise OAuthStateError(f"User not found for id: {user_id}") from e

    def _redirect_with_success(
        self, base_url: str, provider: str, created: bool, expires_at
    ):
        """
        Redirect to frontend with success parameters.

        Args:
            base_url: Frontend callback base URL
            provider: OAuth provider name
            created: Whether this was a new connection
            expires_at: Token expiration datetime or None

        Returns:
            Response: HTTP 302 redirect
        """
        redirect_url = (
            f"{base_url}?success=true&service={provider}&created={str(created).lower()}"
        )
        if expires_at:
            redirect_url += f"&expires_at={expires_at.isoformat()}"

        return Response(
            status=status.HTTP_302_FOUND, headers={"Location": redirect_url}
        )

    def _redirect_with_error(self, base_url: str, error_type: str, message: str):
        """
        Redirect to frontend with error parameters.

        Args:
            base_url: Frontend callback base URL
            error_type: Type of error (invalid_state, oauth_error, etc.)
            message: Human-readable error message

        Returns:
            Response: HTTP 302 redirect
        """
        from urllib.parse import quote

        redirect_url = f"{base_url}?error={error_type}&message={quote(message)}"
        return Response(
            status=status.HTTP_302_FOUND, headers={"Location": redirect_url}
        )


class ServiceConnectionListView(APIView):
    """
    List user's connected OAuth2 services.

    GET /auth/services/

    Returns a list of services the user has connected via OAuth2,
    along with connection status and available providers.

    Returns:
        - connected_services: List of connected services with details
        - available_providers: List of all available OAuth2 providers
        - total_connected: Number of connected services
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ServiceConnectionListSerializer

    def get(self, request):
        """List connected services."""
        try:
            # Get user's connected services
            service_tokens = ServiceToken.objects.filter(user=request.user)

            # Serialize tokens
            token_serializer = ServiceTokenSerializer(service_tokens, many=True)

            # Get available providers
            available_providers = OAuthManager.list_available_providers()

            # Prepare response
            response_data = {
                "connected_services": token_serializer.data,
                "available_providers": available_providers,
                "total_connected": service_tokens.count(),
            }

            serializer = ServiceConnectionListSerializer(response_data)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing services: {str(e)}", exc_info=True)
            return Response(
                {"error": "internal_error", "message": "Failed to list services"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ServiceDisconnectView(APIView):
    """
    Disconnect an OAuth2 service.

    DELETE /auth/services/{provider}/disconnect/

    Revokes the access token (if possible) and removes the connection
    from the database.

    Path Parameters:
        provider: OAuth2 provider name (google, github, etc.)

    Returns:
        - message: Success message
        - service: Provider name
        - revoked_at_provider: Whether token was revoked at provider
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ServiceDisconnectSerializer

    @extend_schema(request=None, responses={200: ServiceDisconnectSerializer})
    def delete(self, request, provider: str):
        """Disconnect a service."""
        try:
            # Check if user has this service connected
            try:
                service_token = ServiceToken.objects.get(
                    user=request.user, service_name=provider
                )
            except ServiceToken.DoesNotExist:
                return Response(
                    {
                        "error": "not_connected",
                        "message": f"You are not connected to {provider}",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Try to revoke token at provider
            revoked_at_provider = False
            try:
                oauth_provider = OAuthManager.get_provider(provider)
                revoked_at_provider = oauth_provider.revoke_token(
                    service_token.access_token
                )
            except Exception as e:
                logger.warning(f"Failed to revoke token at {provider}: {str(e)}")

            # Delete token from database
            service_token.delete()

            logger.info(f"User {request.user.email} disconnected from {provider}")

            response_data = {
                "message": f"Successfully disconnected from {provider}",
                "service": provider,
                "revoked_at_provider": revoked_at_provider,
            }

            serializer = ServiceDisconnectSerializer(response_data)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error disconnecting service: {str(e)}", exc_info=True)
            return Response(
                {"error": "internal_error", "message": "Failed to disconnect service"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConnectionHistoryView(APIView):
    """
    Get connection history for troubleshooting.

    GET /auth/oauth/history/

    Returns recent connection events for the authenticated user.
    Useful for troubleshooting connection issues.

    Query Parameters:
        limit: Maximum number of entries to return (default: 20, max: 50)

    Returns:
        - entries: List of connection history entries
        - total_entries: Total number of entries available
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None  # We'll return raw data

    def get(self, request):
        """Get connection history."""
        try:
            # Get limit parameter
            limit = request.query_params.get('limit', 20)
            try:
                limit = int(limit)
                if limit < 1:
                    limit = 20
                elif limit > 50:
                    limit = 50
            except ValueError:
                limit = 20

            # Get user's OAuth notifications (connection history)
            from .models import OAuthNotification
            notifications = OAuthNotification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:limit]

            # Convert to history entries
            entries = []
            for notification in notifications:
                entry = {
                    'service_name': notification.service_name,
                    'event_type': notification.notification_type,
                    'timestamp': notification.created_at.isoformat(),
                    'message': notification.message,
                    'is_error': notification.notification_type in [
                        'token_expired', 'refresh_failed', 'auth_error'
                    ],
                }
                entries.append(entry)

            # Also add successful connections from ServiceToken
            from .models import ServiceToken
            tokens = ServiceToken.objects.filter(
                user=request.user
            ).order_by('-created_at')[:limit]

            for token in tokens:
                # Only add if not already in notifications
                if not any(e['service_name'] == token.service_name and
                          e['event_type'] == 'connected' for e in entries):
                    entry = {
                        'service_name': token.service_name,
                        'event_type': 'connected',
                        'timestamp': token.created_at.isoformat(),
                        'message': f'Successfully connected to {token.service_name}',
                        'is_error': False,
                    }
                    entries.append(entry)

            # Sort by timestamp (most recent first) and limit
            entries.sort(key=lambda x: x['timestamp'], reverse=True)
            entries = entries[:limit]

            response_data = {
                'entries': entries,
                'total_entries': len(entries),  # Simplified for now
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching connection history: {str(e)}", exc_info=True)
            return Response(
                {"error": "internal_error", "message": "Failed to fetch connection history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
