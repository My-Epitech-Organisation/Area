"""OAuth2 integration package for external service authentication."""

from .base import BaseOAuthProvider
from .exceptions import (
    InvalidProviderError,
    InvalidTokenError,
    OAuthError,
    OAuthStateError,
    ProviderAPIError,
    TokenExchangeError,
    TokenRefreshError,
)
from .github import GitHubOAuthProvider
from .google import GoogleOAuthProvider
from .manager import OAuthManager

__all__ = [
    "BaseOAuthProvider",
    "GoogleOAuthProvider",
    "GitHubOAuthProvider",
    "OAuthManager",
    "OAuthError",
    "InvalidProviderError",
    "OAuthStateError",
    "TokenExchangeError",
    "TokenRefreshError",
    "InvalidTokenError",
    "ProviderAPIError",
]
