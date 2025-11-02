"""Notion OAuth2 provider implementation."""

import logging
from typing import Dict
from urllib.parse import urlencode

import requests

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError

logger = logging.getLogger(__name__)


class NotionOAuthProvider(BaseOAuthProvider):
    """
    Notion OAuth2 provider implementation.

    Notion supports standard OAuth2 with refresh tokens.
    Access tokens expire after 1 hour, refresh tokens are long-lived.

    Scopes typically used:
        - all: Full access to user's workspace
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Notion OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to Notion
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "owner": "user",  # Always user for AREA
        }

        query_string = urlencode(params)
        authorization_url = f"{self.authorization_endpoint}?{query_string}"

        logger.info(f"Generated Notion authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange Notion authorization code for access token.

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
                    "Authorization": f"Basic {self._get_basic_auth()}",
                    "Content-Type": "application/json",
                },
                json={
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
                raise TokenExchangeError(f"Notion error: {error_msg}")

            logger.info("Successfully exchanged Notion authorization code for token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "expires_in": token_data.get("expires_in", 3600),  # Default 1 hour
                "token_type": token_data.get("token_type", "Bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Notion token exchange failed: {str(e)}")
            raise TokenExchangeError(f"Failed to exchange Notion code: {str(e)}") from e

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh Notion access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict with new access_token, refresh_token, expires_in, token_type

        Raises:
            TokenExchangeError: If refresh fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                headers={
                    "Authorization": f"Basic {self._get_basic_auth()}",
                    "Content-Type": "application/json",
                },
                json={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            token_data = response.json()

            if "error" in token_data:
                error_msg = token_data.get("error_description", token_data["error"])
                raise TokenExchangeError(f"Notion refresh error: {error_msg}")

            logger.info("Successfully refreshed Notion access token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "Bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Notion token refresh failed: {str(e)}")
            raise TokenExchangeError(f"Failed to refresh Notion token: {str(e)}") from e

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from Notion.

        Args:
            access_token: Valid Notion access token

        Returns:
            Dict with user information

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            response = requests.get(
                "https://api.notion.com/v1/users/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Notion-Version": "2022-06-28",
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "email": data.get("person", {}).get("email"),
                "avatar_url": data.get("avatar_url"),
                "type": data.get("type"),  # "person" or "bot"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Notion user info: {str(e)}")
            raise ProviderAPIError(f"Failed to get Notion user info: {str(e)}") from e

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Notion access token.

        Note: Notion doesn't provide a direct token revocation endpoint.
        The token will naturally expire.

        Args:
            token: Token to revoke

        Returns:
            bool: Always False as Notion doesn't support revocation
        """
        logger.warning(
            "Notion doesn't support token revocation - tokens expire naturally"
        )
        return False

    def _get_basic_auth(self) -> str:
        """
        Get base64 encoded client_id:client_secret for Basic Auth.

        Returns:
            str: Base64 encoded credentials
        """
        import base64

        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()
