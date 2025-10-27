##
## EPITECH PROJECT, 2025
## Area
## File description:
## spotify
##

"""Spotify OAuth2 provider implementation."""

import logging
from typing import Dict
from urllib.parse import urlencode

import requests

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError

logger = logging.getLogger(__name__)


class SpotifyOAuthProvider(BaseOAuthProvider):
    """
    Spotify OAuth2 provider implementation.

    Spotify supports refresh tokens and follows standard OAuth2 flow.
    Access tokens expire after 1 hour, refresh tokens are long-lived.

    Scopes typically used:
        - user-read-private: Read access to user's subscription details
        - user-read-email: Read access to user's email address
        - user-read-playback-state: Read access to user's current playback state
        - user-modify-playback-state: Control playback on user's active devices
        - user-read-currently-playing: Read access to user's currently playing content
        - playlist-read-private: Read access to user's private playlists
        - playlist-modify-public: Write access to user's public playlists
        - playlist-modify-private: Write access to user's private playlists
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Spotify OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to Spotify
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "show_dialog": "true",  # Force user to re-authorize
        }

        query_string = urlencode(params)
        authorization_url = f"{self.authorization_endpoint}?{query_string}"

        logger.info(f"Generated Spotify authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange Spotify authorization code for access token.

        Args:
            code: Authorization code from callback

        Returns:
            Dict with access_token, refresh_token, expires_in, token_type

        Raises:
            TokenExchangeError: If token exchange fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": self._get_basic_auth_header(),
                },
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                timeout=30,
            )

            response.raise_for_status()
            token_data = response.json()

            # Check for error in response
            if "error" in token_data:
                error_msg = token_data.get("error_description", token_data["error"])
                raise TokenExchangeError(f"Spotify error: {error_msg}")

            logger.info("Successfully exchanged Spotify authorization code for token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "expires_in": token_data["expires_in"],
                "token_type": token_data.get("token_type", "Bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Spotify token exchange failed: {str(e)}")
            raise TokenExchangeError(
                f"Failed to exchange Spotify code: {str(e)}"
            ) from e

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh Spotify access token.

        Args:
            refresh_token: The refresh token

        Returns:
            Dict with new access_token, refresh_token, expires_in, token_type

        Raises:
            TokenExchangeError: If refresh fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": self._get_basic_auth_header(),
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            token_data = response.json()

            # Check for error in response
            if "error" in token_data:
                error_msg = token_data.get("error_description", token_data["error"])
                raise TokenExchangeError(f"Spotify refresh error: {error_msg}")

            logger.info("Successfully refreshed Spotify access token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get(
                    "refresh_token", refresh_token
                ),  # May be rotated
                "expires_in": token_data["expires_in"],
                "token_type": token_data.get("token_type", "Bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Spotify token refresh failed: {str(e)}")
            raise TokenExchangeError(
                f"Failed to refresh Spotify token: {str(e)}"
            ) from e

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from Spotify.

        Args:
            access_token: Valid Spotify access token

        Returns:
            Dict with id, email, display_name, images, etc.

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            response = requests.get(
                self.userinfo_endpoint or "https://api.spotify.com/v1/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            return {
                "id": data.get("id"),
                "email": data.get("email"),
                "display_name": data.get("display_name"),
                "images": data.get("images", []),
                "country": data.get("country"),
                "product": data.get("product"),  # premium, free, etc.
                "followers": data.get("followers", {}).get("total", 0),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Spotify user info: {str(e)}")
            raise ProviderAPIError(f"Failed to get Spotify user info: {str(e)}") from e

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Spotify access token.

        Note: Spotify doesn't have a direct token revocation endpoint.
        The token will naturally expire, but we can mark it as invalid locally.

        Args:
            token: Token to revoke

        Returns:
            bool: Always returns True (Spotify doesn't support revocation)
        """
        logger.info("Spotify token revocation requested - tokens expire naturally")
        # Spotify doesn't provide a token revocation endpoint
        # Tokens expire after 1 hour naturally
        return True

    def _get_basic_auth_header(self) -> str:
        """
        Generate Basic Auth header for Spotify API calls.

        Returns:
            str: Basic Auth header value
        """
        import base64

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
