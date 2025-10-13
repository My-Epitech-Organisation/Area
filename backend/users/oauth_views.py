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
from .oauth.exceptions import InvalidProviderError, OAuthError
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
    Handle OAuth2 authorization callback.

    GET /auth/oauth/{provider}/callback/?code=xxx&state=yyy

    Exchanges the authorization code for an access token and stores it.
    This endpoint is called by the OAuth2 provider after user authorization.

    Path Parameters:
        provider: OAuth2 provider name (google, github, etc.)

    Query Parameters:
        code: Authorization code (on success)
        state: CSRF protection token (on success)
        error: Error code (on failure)
        error_description: Error description (on failure)

    Returns:
        - message: Success/error message
        - service: Provider name
        - created: Whether this is a new connection
        - expires_at: Token expiration timestamp (if applicable)
    """

    # NOTE: We intentionally do NOT require IsAuthenticated for the callback
    # because the OAuth provider will redirect the browser to this endpoint
    # without an Authorization header. We support two modes:
    # 1) Browser navigation: no Authorization header and Accept prefers HTML ->
    #    we validate the state, look up the user_id stored in cache and complete
    #    the flow on behalf of that user, then redirect to the frontend callback
    #    route so the SPA can show a success page.
    # 2) API/AJAX client: includes Authorization header or X-Requested-With ->
    #    we require authentication and behave as before returning JSON.
    # Override global DEFAULT_PERMISSION_CLASSES (IsAuthenticated) so that
    # providers can redirect the browser here without a Bearer token.
    permission_classes = [AllowAny]
    serializer_class = OAuthCallbackSerializer

    def get(self, request, provider: str):
        """Process OAuth2 callback and exchange code for token.

        Support both browser redirects (no auth header) and API calls
        (with Authorization header)."""

        # Validate callback parameters first
        serializer = OAuthCallbackSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {"error": "invalid_callback", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # If provider returned an error, show it
        if validated_data.get("error"):
            error_msg = validated_data.get("error_description", validated_data["error"])
            logger.warning(f"OAuth2 callback error for {provider}: {error_msg}")
            return Response(
                {"error": validated_data["error"], "message": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = validated_data["code"]
        state = validated_data["state"]

        # Determine whether this is a browser navigation or an API/fetch call
        has_auth = bool(
            request.headers.get("Authorization")
            or request.headers.get("X-Requested-With")
        )
        accepts_html = "text/html" in request.headers.get("Accept", "")

        # If this looks like an API call, require authentication
        if has_auth:
            # API mode - behave like before (require authenticated user)
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                # Validate CSRF state against this user's id
                is_valid, error_msg = OAuthManager.validate_state(
                    state=state, user_id=str(request.user.id), provider=provider
                )

                if not is_valid:
                    logger.warning(
                        f"Invalid OAuth2 state for user {request.user.email}: {error_msg}"
                    )
                    return Response(
                        {"error": "invalid_state", "message": error_msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                oauth_provider = OAuthManager.get_provider(provider)
                token_data = oauth_provider.exchange_code_for_token(code)
                expires_at = oauth_provider.calculate_expiry(
                    token_data.get("expires_in")
                )

                service_token, created = ServiceToken.objects.update_or_create(
                    user=request.user,
                    service_name=provider,
                    defaults={
                        "access_token": token_data["access_token"],
                        "refresh_token": token_data.get("refresh_token", ""),
                        "expires_at": expires_at,
                    },
                )

                action = "connected" if created else "reconnected"
                logger.info(f"User {request.user.email} {action} to {provider}")

                return Response(
                    {
                        "message": f"Successfully {action} to {provider}",
                        "service": provider,
                        "created": created,
                        "expires_at": expires_at.isoformat() if expires_at else None,
                    },
                    status=status.HTTP_200_OK,
                )

            except OAuthError as e:
                logger.error(f"OAuth2 error during callback: {str(e)}")
                return Response(
                    {"error": "oauth_error", "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error in OAuth2 callback: {str(e)}", exc_info=True
                )
                return Response(
                    {
                        "error": "internal_error",
                        "message": "Failed to complete OAuth2 flow",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Browser navigation mode - complete flow on behalf of user stored in state
        try:
            # Validate state: read cached state to find the initiating user
            from django.core.cache import cache as _cache

            cache_key = OAuthManager._get_state_cache_key(state)
            state_data = _cache.get(cache_key)

            if not state_data:
                # If invalid state, return JSON for API clients or redirect to frontend with error
                logger.warning(
                    f"OAuth2 state missing or expired for provider {provider}"
                )
                if accepts_html:
                    frontend = getattr(
                        settings, "FRONTEND_URL", None
                    ) or request.build_absolute_uri("/").rstrip("/")
                    redirect_to = (
                        f"{frontend}/auth/callback/{provider}?error=invalid_state"
                    )
                    return Response(
                        status=status.HTTP_302_FOUND, headers={"Location": redirect_to}
                    )
                return Response(
                    {"error": "invalid_state", "message": "State invalid or expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_id = state_data.get("user_id")
            if not user_id:
                logger.warning("State missing user_id")
                return Response(
                    {
                        "error": "invalid_state",
                        "message": "State missing user information",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Now validate state atomically (this will also delete it from cache)
            is_valid, err = OAuthManager.validate_state(
                state=state, user_id=str(user_id), provider=provider
            )
            if not is_valid:
                logger.warning(f"State validation failed after lookup: {err}")
                if accepts_html:
                    frontend = getattr(
                        settings, "FRONTEND_URL", None
                    ) or request.build_absolute_uri("/").rstrip("/")
                    redirect_to = (
                        f"{frontend}/auth/callback/{provider}?error=invalid_state"
                    )
                    return Response(
                        status=status.HTTP_302_FOUND, headers={"Location": redirect_to}
                    )
                return Response(
                    {"error": "invalid_state", "message": err},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Load user by id with proper UUID validation
            from django.contrib.auth import get_user_model
            from django.shortcuts import get_object_or_404

            User = get_user_model()
            try:
                # Validate that user_id is a valid UUID (User.id is a UUIDField)
                user_uuid = UUID(user_id)
                user = get_object_or_404(User, id=user_uuid)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid UUID from OAuth state: {user_id} - {e}")
                return Response(
                    {"error": "invalid_state", "message": "Invalid user identifier"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                logger.error(f"User lookup failed for id {user_id}: {e}")
                return Response(
                    {"error": "invalid_state", "message": "User not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            oauth_provider = OAuthManager.get_provider(provider)
            token_data = oauth_provider.exchange_code_for_token(code)
            expires_at = oauth_provider.calculate_expiry(token_data.get("expires_in"))

            service_token, created = ServiceToken.objects.update_or_create(
                user=user,
                service_name=provider,
                defaults={
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token", ""),
                    "expires_at": expires_at,
                },
            )

            action = "connected" if created else "reconnected"
            logger.info(
                f"User {user.email} {action} to {provider} via browser callback"
            )

            # Redirect to frontend callback route with summary params
            frontend = getattr(
                settings, "FRONTEND_URL", None
            ) or request.build_absolute_uri("/").rstrip("/")
            redirect_to = f"{frontend}/auth/callback/{provider}?service={provider}&created={str(created).lower()}"
            if expires_at:
                redirect_to += f"&expires_at={expires_at.isoformat()}"

            return Response(
                status=status.HTTP_302_FOUND, headers={"Location": redirect_to}
            )

        except OAuthError as e:
            logger.error(f"OAuth2 error during browser callback: {str(e)}")
            if accepts_html:
                frontend = getattr(
                    settings, "FRONTEND_URL", None
                ) or request.build_absolute_uri("/").rstrip("/")
                redirect_to = f"{frontend}/auth/callback/{provider}?error=oauth_error"
                return Response(
                    status=status.HTTP_302_FOUND, headers={"Location": redirect_to}
                )
            return Response(
                {"error": "oauth_error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in browser OAuth2 callback: {str(e)}", exc_info=True
            )
            if accepts_html:
                frontend = getattr(
                    settings, "FRONTEND_URL", None
                ) or request.build_absolute_uri("/").rstrip("/")
                redirect_to = (
                    f"{frontend}/auth/callback/{provider}?error=internal_error"
                )
                return Response(
                    status=status.HTTP_302_FOUND, headers={"Location": redirect_to}
                )
            return Response(
                {
                    "error": "internal_error",
                    "message": "Failed to complete OAuth2 flow",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
