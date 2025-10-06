"""API views for OAuth2 authentication flow."""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
                f"User {request.user.username} initiated OAuth2 flow for {provider}"
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

    permission_classes = [IsAuthenticated]

    def get(self, request, provider: str):
        """Process OAuth2 callback and exchange code for token."""
        # Validate callback parameters
        serializer = OAuthCallbackSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                {"error": "invalid_callback", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data

        # Check for OAuth error
        if validated_data.get("error"):
            error_msg = validated_data.get("error_description", validated_data["error"])
            logger.warning(f"OAuth2 callback error for {provider}: {error_msg}")
            return Response(
                {
                    "error": validated_data["error"],
                    "message": error_msg,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = validated_data["code"]
        state = validated_data["state"]

        try:
            # Validate CSRF state
            is_valid, error_msg = OAuthManager.validate_state(
                state=state, user_id=str(request.user.id), provider=provider
            )

            if not is_valid:
                logger.warning(
                    f"Invalid OAuth2 state for user {request.user.username}: {error_msg}"
                )
                return Response(
                    {"error": "invalid_state", "message": error_msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get OAuth provider
            oauth_provider = OAuthManager.get_provider(provider)

            # Exchange authorization code for access token
            token_data = oauth_provider.exchange_code_for_token(code)

            # Calculate expiration
            expires_at = oauth_provider.calculate_expiry(token_data["expires_in"])

            # Store or update token in database
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
            logger.info(f"User {request.user.username} {action} to {provider}")

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

            logger.info(f"User {request.user.username} disconnected from {provider}")

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
