"""Base OAuth2 provider abstract class using Template Method pattern."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Optional

from django.utils import timezone


class BaseOAuthProvider(ABC):
    """
    Abstract base class for OAuth2 providers.

    Implements the Template Method pattern to provide a consistent interface
    for different OAuth2 providers (Google, GitHub, etc.).

    Each provider must implement the abstract methods to handle
    provider-specific OAuth2 flows.
    """

    def __init__(self, config: Dict):
        """
        Initialize provider with configuration.

        Args:
            config: Dictionary containing OAuth2 configuration:
                - client_id: OAuth2 client ID
                - client_secret: OAuth2 client secret
                - redirect_uri: Callback URL after authorization
                - authorization_endpoint: Provider's authorization URL
                - token_endpoint: Provider's token exchange URL
                - userinfo_endpoint: Provider's user info URL (optional)
                - scopes: List of OAuth2 scopes to request
                - requires_refresh: Whether provider supports refresh tokens
        """
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.redirect_uri = config["redirect_uri"]
        self.authorization_endpoint = config["authorization_endpoint"]
        self.token_endpoint = config["token_endpoint"]
        self.userinfo_endpoint = config.get("userinfo_endpoint")
        self.scopes = config.get("scopes", [])
        self.requires_refresh = config.get("requires_refresh", True)

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL with state parameter.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to
        """
        pass

    @abstractmethod
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code received from callback

        Returns:
            Dict containing:
                - access_token: The access token
                - refresh_token: Refresh token (if supported)
                - expires_in: Token expiration in seconds
                - token_type: Token type (usually 'Bearer')

        Raises:
            TokenExchangeError: If token exchange fails
        """
        pass

    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token.

        Args:
            refresh_token: The refresh token

        Returns:
            Dict containing:
                - access_token: New access token
                - expires_in: Token expiration in seconds

        Raises:
            TokenRefreshError: If refresh fails
            NotImplementedError: If provider doesn't support refresh
        """
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from the provider.

        Args:
            access_token: Valid access token

        Returns:
            Dict containing user information (provider-specific fields)

        Raises:
            ProviderAPIError: If API call fails
        """
        pass

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if revocation successful, False otherwise
        """
        pass

    def calculate_expiry(self, expires_in: int) -> datetime:
        """
        Calculate token expiration datetime.

        Args:
            expires_in: Number of seconds until expiration

        Returns:
            datetime: Expiration timestamp (timezone-aware)
        """
        return timezone.now() + timedelta(seconds=expires_in)

    def is_token_expired(self, expires_at: Optional[datetime]) -> bool:
        """
        Check if a token is expired.

        Args:
            expires_at: Token expiration datetime

        Returns:
            bool: True if expired, False otherwise
        """
        if not expires_at:
            return False
        return timezone.now() >= expires_at

    def __str__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(client_id={self.client_id[:10]}...)"
