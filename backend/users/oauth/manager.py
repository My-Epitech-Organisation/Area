"""OAuth2 manager for provider orchestration and token management."""

import hashlib
import logging
import secrets
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from users.models import ServiceToken

from .exceptions import InvalidProviderError, InvalidTokenError, TokenRefreshError
from .github import GitHubOAuthProvider
from .google import GoogleOAuthProvider

logger = logging.getLogger(__name__)


class OAuthManager:
    """
    Manages OAuth2 providers and token lifecycle.

    Implements Factory pattern for provider instantiation and handles:
    - Provider registration and retrieval
    - Token validation and automatic refresh
    - CSRF state generation and validation
    """

    _providers = {}
    _provider_classes = {
        "google": GoogleOAuthProvider,
        "github": GitHubOAuthProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str):
        """
        Get or create an OAuth2 provider instance.

        Uses lazy initialization and caching for performance.

        Args:
            provider_name: Name of the provider (e.g., 'google', 'github')

        Returns:
            BaseOAuthProvider: Provider instance

        Raises:
            InvalidProviderError: If provider not configured or not implemented
        """
        # Return cached provider if available
        if provider_name in cls._providers:
            return cls._providers[provider_name]

        # Get configuration
        config = settings.OAUTH2_PROVIDERS.get(provider_name)
        if not config:
            raise InvalidProviderError(
                f"Provider '{provider_name}' is not configured in settings"
            )

        # Validate required fields
        required_fields = ["client_id", "client_secret", "redirect_uri"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            raise InvalidProviderError(
                f"Provider '{provider_name}' is missing configuration: {', '.join(missing_fields)}"
            )

        # Get provider class
        provider_class = cls._provider_classes.get(provider_name)
        if not provider_class:
            raise InvalidProviderError(
                f"Provider '{provider_name}' is not implemented. "
                f"Available providers: {', '.join(cls._provider_classes.keys())}"
            )

        # Instantiate and cache provider
        cls._providers[provider_name] = provider_class(config)
        logger.info(f"Initialized OAuth2 provider: {provider_name}")

        return cls._providers[provider_name]

    @classmethod
    def get_valid_token(cls, user, service_name: str) -> Optional[str]:
        """
        Get a valid access token for a user and service.

        Automatically refreshes expired tokens if refresh token is available.

        Args:
            user: Django User instance
            service_name: Name of the service (e.g., 'google', 'github')

        Returns:
            str: Valid access token, or None if not available/refresh failed

        Raises:
            InvalidProviderError: If service_name is not a valid provider
        """
        try:
            service_token = ServiceToken.objects.get(
                user=user, service_name=service_name
            )
        except ServiceToken.DoesNotExist:
            logger.debug(
                f"No token found for user {user.username} and service {service_name}"
            )
            return None

        # Check if token is expired
        if service_token.expires_at and timezone.now() >= service_token.expires_at:
            logger.info(
                f"Token expired for {user.username}/{service_name}, attempting refresh"
            )

            # Try to refresh if refresh token exists
            if service_token.refresh_token:
                try:
                    provider = cls.get_provider(service_name)

                    # Some providers don't support refresh
                    if not provider.requires_refresh:
                        logger.warning(
                            f"Provider {service_name} doesn't support token refresh"
                        )
                        return service_token.access_token  # Token might still be valid

                    # Perform refresh
                    refreshed = provider.refresh_access_token(
                        service_token.refresh_token
                    )

                    # Update token in database
                    service_token.access_token = refreshed["access_token"]
                    service_token.expires_at = provider.calculate_expiry(
                        refreshed["expires_in"]
                    )
                    service_token.save(update_fields=["access_token", "expires_at"])

                    logger.info(f"Successfully refreshed token for {service_name}")
                    return service_token.access_token

                except TokenRefreshError as e:
                    logger.error(
                        f"Failed to refresh token for {user.username}/{service_name}: {e}"
                    )
                    return None
                except NotImplementedError:
                    # Provider doesn't support refresh (e.g., GitHub)
                    return service_token.access_token
            else:
                logger.warning(
                    f"Token expired for {service_name} but no refresh token available"
                )
                return None

        # Token is valid
        return service_token.access_token

    @classmethod
    def generate_state(cls, user_id: str, provider: str) -> str:
        """
        Generate a cryptographically secure CSRF state token.

        The state is stored in cache with an expiration time for later validation.

        Args:
            user_id: User ID to associate with the state
            provider: Provider name

        Returns:
            str: Secure random state string
        """
        # Generate random state
        state = secrets.token_urlsafe(32)

        # Create cache key
        cache_key = cls._get_state_cache_key(state)

        # Store state data in cache with expiration
        state_data = {
            "user_id": str(user_id),
            "provider": provider,
            "created_at": timezone.now().isoformat(),
        }

        # Default expiration: 10 minutes
        expiry = getattr(settings, "OAUTH2_STATE_EXPIRY", 600)
        cache.set(cache_key, state_data, timeout=expiry)

        logger.debug(f"Generated OAuth2 state for user {user_id}, provider {provider}")
        return state

    @classmethod
    def validate_state(
        cls, state: str, user_id: str, provider: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate an OAuth2 state token.

        Args:
            state: State token to validate
            user_id: Expected user ID
            provider: Expected provider name

        Returns:
            tuple: (is_valid, error_message)
                - is_valid: True if state is valid
                - error_message: Error description if invalid, None if valid
        """
        cache_key = cls._get_state_cache_key(state)
        state_data = cache.get(cache_key)

        if not state_data:
            return False, "State token is invalid or expired"

        # Validate user ID
        if state_data.get("user_id") != str(user_id):
            return False, "State token user mismatch"

        # Validate provider
        if state_data.get("provider") != provider:
            return False, "State token provider mismatch"

        # State is valid, delete it (one-time use)
        cache.delete(cache_key)

        return True, None

    @classmethod
    def _get_state_cache_key(cls, state: str) -> str:
        """
        Generate a cache key for OAuth2 state.

        Args:
            state: State token

        Returns:
            str: Cache key
        """
        # Hash the state for shorter cache key
        state_hash = hashlib.sha256(state.encode()).hexdigest()[:16]
        return f"oauth2_state_{state_hash}"

    @classmethod
    def revoke_user_token(cls, user, service_name: str) -> bool:
        """
        Revoke a user's token for a service.

        Args:
            user: Django User instance
            service_name: Service name

        Returns:
            bool: True if successfully revoked, False otherwise
        """
        try:
            service_token = ServiceToken.objects.get(
                user=user, service_name=service_name
            )

            # Try to revoke at provider
            try:
                provider = cls.get_provider(service_name)
                provider.revoke_token(service_token.access_token)
            except Exception as e:
                logger.warning(
                    f"Failed to revoke token at provider {service_name}: {e}"
                )

            # Delete from database
            service_token.delete()
            logger.info(f"Revoked token for {user.username}/{service_name}")
            return True

        except ServiceToken.DoesNotExist:
            logger.warning(
                f"No token to revoke for {user.username}/{service_name}"
            )
            return False
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    @classmethod
    def list_available_providers(cls) -> list[str]:
        """
        Get list of configured and implemented providers.

        Returns:
            list: Available provider names
        """
        return list(cls._provider_classes.keys())

    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """
        Check if a provider is configured and available.

        Args:
            provider_name: Provider name

        Returns:
            bool: True if available, False otherwise
        """
        if provider_name not in cls._provider_classes:
            return False

        config = settings.OAUTH2_PROVIDERS.get(provider_name, {})
        return bool(config.get("client_id") and config.get("client_secret"))
