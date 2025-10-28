"""OAuth2 manager for provider orchestration and token management."""

import hashlib
import logging
import secrets
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from users.models import ServiceToken

from .exceptions import InvalidProviderError, TokenRefreshError
from .github import GitHubOAuthProvider
from .google import GoogleOAuthProvider
from .slack import SlackOAuthProvider
from .spotify import SpotifyOAuthProvider
from .twitch import TwitchOAuthProvider

logger = logging.getLogger(__name__)
User = get_user_model()


def _create_token_refresh_notification(service_token: ServiceToken, error: str) -> None:
    """
    Create a notification when token refresh fails.

    Args:
        service_token: ServiceToken that failed to refresh
        error: Error message describing the failure
    """
    from users.models import OAuthNotification

    message = (
        f"Your {service_token.service_name} connection has expired and "
        f"could not be automatically refreshed. Please reconnect your account "
        f"to continue using {service_token.service_name} services.\n\n"
        f"Error: {error}"
    )

    OAuthNotification.create_notification(
        user=service_token.user,
        service_name=service_token.service_name,
        notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
        message=message,
    )
    logger.info(
        f"Created notification for {service_token.user.username}/{service_token.service_name}"
    )


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
        "slack": SlackOAuthProvider,
        "spotify": SpotifyOAuthProvider,
        "twitch": TwitchOAuthProvider,
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
                f"Provider '{provider_name}' is missing configuration: "
                f"{', '.join(missing_fields)}"
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

        Automatically refreshes expired tokens or tokens expiring soon
        (within 5 minutes) if refresh token is available. This proactive
        approach prevents API calls from failing due to token expiration.

        Args:
            user: Django User instance
            service_name: Name of the service (e.g., 'google', 'github')

        Returns:
            str: Valid access token, or None if not available/refresh failed

        Raises:
            InvalidProviderError: If service_name is not a valid provider

        Example:
            >>> token = OAuthManager.get_valid_token(user, "google")
            >>> if token:
            ...     headers = {"Authorization": f"Bearer {token}"}
            ...     response = requests.get(api_url, headers=headers)
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

        # Check if token needs refresh (expired or expiring soon)
        if service_token.is_expired or service_token.needs_refresh:
            refresh_status = "expired" if service_token.is_expired else "expiring soon"
            logger.info(
                f"Token {refresh_status} for {user.username}/{service_name}, "
                f"attempting refresh"
            )

            # Try to refresh if refresh token exists
            if service_token.refresh_token:
                refreshed_token = cls.refresh_if_needed(service_token)
                if refreshed_token:
                    # Mark token as used and return
                    service_token.mark_used()
                    return refreshed_token
                else:
                    # Refresh failed
                    logger.error(
                        f"Token refresh failed for {user.username}/{service_name}"
                    )
                    return None
            else:
                logger.warning(
                    f"Token {refresh_status} for {service_name} "
                    f"but no refresh token available"
                )
                return None

        # Token is valid - mark as used and return
        service_token.mark_used()
        return service_token.access_token

    @classmethod
    def refresh_if_needed(cls, service_token: ServiceToken) -> Optional[str]:
        """
        Refresh an OAuth2 token if it's expired or expiring soon.

        This method handles the token refresh logic including error handling,
        database updates, and provider-specific behavior.

        Args:
            service_token: ServiceToken instance to refresh

        Returns:
            str: New access token if refresh successful, None otherwise

        Example:
            >>> service_token = ServiceToken.objects.get(user=user, service_name="google")
            >>> new_token = OAuthManager.refresh_if_needed(service_token)
            >>> if new_token:
            ...     print("Token refreshed successfully")
        """
        service_name = service_token.service_name

        try:
            provider = cls.get_provider(service_name)

            # Some providers don't support refresh (e.g., GitHub)
            if not provider.requires_refresh:
                logger.debug(
                    f"Provider {service_name} doesn't support token refresh "
                    f"(tokens are long-lived)"
                )
                # Return existing token - it might still be valid
                return service_token.access_token

            # Perform refresh
            refreshed = provider.refresh_access_token(service_token.refresh_token)

            # Update token in database
            service_token.access_token = refreshed["access_token"]

            # Update refresh token if provided (some providers rotate it)
            if "refresh_token" in refreshed:
                service_token.refresh_token = refreshed["refresh_token"]

            # Update expiry
            if "expires_in" in refreshed:
                service_token.expires_at = provider.calculate_expiry(
                    refreshed["expires_in"]
                )

            # Update token type if provided
            if "token_type" in refreshed:
                service_token.token_type = refreshed["token_type"]

            # Save with all updated fields
            service_token.save(
                update_fields=[
                    "access_token",
                    "refresh_token",
                    "expires_at",
                    "token_type",
                    "updated_at",  # auto_now field
                ]
            )

            logger.info(
                f"Successfully refreshed token for {service_name} "
                f"(user: {service_token.user.username})"
            )
            return service_token.access_token

        except TokenRefreshError as e:
            error_msg = str(e)
            logger.error(
                f"Failed to refresh token for {service_name} "
                f"(user: {service_token.user.username}): {error_msg}"
            )
            # Create notification for user
            _create_token_refresh_notification(service_token, error_msg)
            return None
        except NotImplementedError:
            # Provider doesn't support refresh
            logger.warning(
                f"Token refresh not implemented for {service_name}, "
                f"returning existing token"
            )
            return service_token.access_token
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                f"Unexpected error refreshing token for {service_name}: {e}",
                exc_info=True,
            )
            # Create notification for unexpected errors too
            _create_token_refresh_notification(service_token, error_msg)
            return None

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
            logger.warning(f"No token to revoke for {user.username}/{service_name}")
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
        return bool(
            config.get("client_id")
            and config.get("client_secret")
            and config.get("redirect_uri")
        )

    @classmethod
    def get_or_create_google_user(
        cls,
        email: str,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
        email_verified: bool = False,
        picture: Optional[str] = None,
    ):
        """
        Get or create a user from Google authentication data.

        This method is used by both OAuth2 flow (web) and Google Sign-In (mobile)
        to ensure consistent user creation logic.

        Args:
            email: User's email address from Google
            google_id: Google user ID (sub claim)
            name: User's display name from Google
            email_verified: Whether Google has verified the email
            picture: URL to user's Google profile picture

        Returns:
            Tuple[User, bool]: (user instance, created flag)
                - user: The User instance
                - created: True if user was created, False if existing

        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError("Email is required to create or retrieve a Google user")

        created = False

        try:
            # Try to find existing user by email
            user = User.objects.get(email=email)
            logger.info(f"Existing user logged in with Google: {email}")

        except User.DoesNotExist:
            # Create new user
            username = email.split("@")[0]

            # Ensure username is unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Create user without password (OAuth-only account)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,  # No password for OAuth users
            )

            # Set optional fields if provided
            if name:
                # Split name into first_name and last_name
                name_parts = name.split(" ", 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]

            # Mark email as verified if Google confirms it
            if email_verified and hasattr(user, "email_verified"):
                user.email_verified = True

            user.save()
            created = True

            logger.info(f"New user created via Google authentication: {email}")

        return user, created

    @classmethod
    def get_or_create_github_user(
        cls,
        github_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ):
        """
        Get or create a user from GitHub authentication data.

        This method ensures consistent user creation logic for GitHub OAuth.

        Args:
            github_id: GitHub user ID (required)
            email: User's email address from GitHub
            username: GitHub username
            name: User's display name from GitHub
            avatar_url: URL to user's GitHub avatar

        Returns:
            Tuple[User, bool]: (user instance, created flag)
                - user: The User instance
                - created: True if user was created, False if existing

        Raises:
            ValueError: If neither github_id nor email is provided
        """
        if not github_id and not email:
            raise ValueError(
                "Either github_id or email is required to \
                create or retrieve a GitHub user"
            )

        created = False

        try:
            # Try to find existing user by email first (if provided)
            if email:
                user = User.objects.get(email=email)
                logger.info(f"Existing user logged in with GitHub: {email}")
            else:
                # Try to find by username if no email
                if username:
                    user = User.objects.get(username=username)
                    logger.info(f"Existing user logged in with GitHub: {username}")
                else:
                    raise User.DoesNotExist

        except User.DoesNotExist:
            # Create new user
            # Use GitHub username or generate from email or github_id
            if username:
                user_username = username
            elif email:
                user_username = email.split("@")[0]
            else:
                user_username = f"github_{github_id}"

            # Ensure username is unique
            base_username = user_username
            counter = 1
            while User.objects.filter(username=user_username).exists():
                user_username = f"{base_username}{counter}"
                counter += 1

            # Create user without password (OAuth-only account)
            user = User.objects.create_user(
                username=user_username,
                email=email or f"github_{github_id}@noreply.github.com",
                password=None,  # No password for OAuth users
            )

            # Set optional fields if provided
            if name:
                # Split name into first_name and last_name
                name_parts = name.split(" ", 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]

            user.save()
            created = True

            logger.info(f"New user created via GitHub \
                authentication: {user.username}")

        return user, created
