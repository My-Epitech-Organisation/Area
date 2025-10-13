"""Custom exceptions for OAuth2 operations."""


class OAuthError(Exception):
    """Base exception for all OAuth2-related errors."""

    pass


class InvalidProviderError(OAuthError):
    """Raised when an unsupported OAuth2 provider is requested."""

    pass


class OAuthStateError(OAuthError):
    """Raised when the OAuth2 state parameter is invalid or expired."""

    pass


class TokenExchangeError(OAuthError):
    """Raised when exchanging authorization code for token fails."""

    pass


class TokenRefreshError(OAuthError):
    """Raised when refreshing an access token fails."""

    pass


class InvalidTokenError(OAuthError):
    """Raised when a token is invalid or expired and cannot be refreshed."""

    pass


class ProviderAPIError(OAuthError):
    """Raised when a provider's API returns an error."""

    pass
