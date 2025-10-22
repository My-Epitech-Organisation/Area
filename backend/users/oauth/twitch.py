"""Twitch OAuth2 provider implementation."""

import logging
from typing import Dict
from urllib.parse import urlencode

import requests

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError, TokenRefreshError

logger = logging.getLogger(__name__)


class TwitchOAuthProvider(BaseOAuthProvider):
    """
    Twitch OAuth2 provider implementation.

    Twitch supports refresh tokens for maintaining long-lived access.
    Access tokens expire after a configurable time period.

    Scopes typically used:
        - user:read:email: Read user email address
        - channel:read:subscriptions: View subscription information
        - channel:manage:broadcast: Manage broadcast settings
        - chat:read: View chat messages
        - chat:edit: Send chat messages
        - clips:edit: Create clips
        - moderator:read:followers: View follower information

    API Documentation: https://dev.twitch.tv/docs/api/
    OAuth Documentation: https://dev.twitch.tv/docs/authentication/
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Twitch OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to Twitch
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            # Force verification prompt to ensure refresh token is provided
            "force_verify": "true",
        }

        query_string = urlencode(params)
        authorization_url = f"{self.authorization_endpoint}?{query_string}"

        logger.info(f"Generated Twitch authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange Twitch authorization code for access token.

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
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30,
            )

            response.raise_for_status()
            token_data = response.json()

            # Check for error in response
            if "error" in token_data:
                error_msg = token_data.get("message", token_data["error"])
                raise TokenExchangeError(f"Twitch error: {error_msg}")

            logger.info("Successfully exchanged Twitch authorization code for token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch token exchange failed: {str(e)}")
            raise TokenExchangeError(f"Failed to exchange Twitch code: {str(e)}") from e

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh Twitch access token using refresh token.

        Args:
            refresh_token: Twitch refresh token

        Returns:
            Dict with new access_token, refresh_token, and expires_in

        Raises:
            TokenRefreshError: If refresh fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30,
            )

            response.raise_for_status()
            token_data = response.json()

            # Check for error in response
            if "error" in token_data:
                error_msg = token_data.get("message", token_data["error"])
                raise TokenRefreshError(f"Twitch error: {error_msg}")

            logger.info("Successfully refreshed Twitch access token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in", 3600),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch token refresh failed: {str(e)}")
            raise TokenRefreshError(f"Failed to refresh Twitch token: {str(e)}") from e

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from Twitch.

        Args:
            access_token: Valid Twitch access token

        Returns:
            Dict with user data: id, login, display_name, email, profile_image_url

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            response = requests.get(
                self.userinfo_endpoint or "https://api.twitch.tv/helix/users",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Client-Id": self.client_id,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            # Twitch returns user info in a "data" array
            if not data.get("data"):
                raise ProviderAPIError("No user data returned from Twitch")

            user_data = data["data"][0]

            return {
                "id": user_data["id"],
                "login": user_data["login"],
                "display_name": user_data["display_name"],
                "email": user_data.get("email", ""),
                "profile_image_url": user_data.get("profile_image_url", ""),
                "broadcaster_type": user_data.get("broadcaster_type", ""),
                "description": user_data.get("description", ""),
                "view_count": user_data.get("view_count", 0),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch get_user_info failed: {str(e)}")
            raise ProviderAPIError(f"Failed to get Twitch user info: {str(e)}") from e

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Twitch access token.

        Args:
            token: Access token to revoke

        Returns:
            bool: True if revocation successful, False otherwise
        """
        try:
            response = requests.post(
                "https://id.twitch.tv/oauth2/revoke",
                data={
                    "client_id": self.client_id,
                    "token": token,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30,
            )

            # Twitch returns 200 for successful revocation
            if response.status_code == 200:
                logger.info("Successfully revoked Twitch token")
                return True
            else:
                logger.warning(
                    f"Twitch token revocation returned status {response.status_code}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch token revocation failed: {str(e)}")
            return False

    def validate_token(self, access_token: str) -> Dict:
        """
        Validate a Twitch access token.

        Args:
            access_token: Token to validate

        Returns:
            Dict with token validation info: client_id, login, scopes, user_id, expires_in

        Raises:
            ProviderAPIError: If validation fails
        """
        try:
            response = requests.get(
                "https://id.twitch.tv/oauth2/validate",
                headers={
                    "Authorization": f"OAuth {access_token}",
                },
                timeout=30,
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitch token validation failed: {str(e)}")
            raise ProviderAPIError(f"Failed to validate Twitch token: {str(e)}") from e
