"""Slack OAuth2 provider implementation."""

import logging
from typing import Dict
from urllib.parse import urlencode

import requests

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError, TokenRefreshError

logger = logging.getLogger(__name__)


class SlackOAuthProvider(BaseOAuthProvider):
    """
    Slack OAuth2 provider implementation.

    Slack supports refresh tokens for maintaining long-lived access.
    Access tokens expire after a configurable time period.

    Scopes typically used:
        - channels:read: Read public channel information
        - channels:write: Create and manage public channels
        - chat:write: Send messages to channels
        - chat:write.public: Send messages to public channels
        - groups:read: Read private channel information
        - groups:write: Create and manage private channels
        - im:read: Read direct messages
        - im:write: Send direct messages
        - mpim:read: Read group direct messages
        - mpim:write: Send group direct messages
        - users:read: Read user information
        - users:read.email: Read user email addresses

    API Documentation: https://api.slack.com/
    OAuth Documentation: https://api.slack.com/authentication/oauth-v2
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Slack OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to Slack
        """
        params = {
            "client_id": self.client_id,
            "scope": ",".join(self.scopes),  # Slack uses comma-separated scopes
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
        }

        query_string = urlencode(params)
        authorization_url = f"{self.authorization_endpoint}?{query_string}"

        logger.info(f"Generated Slack authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange Slack authorization code for access token.

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
            if not token_data.get("ok"):
                error_msg = token_data.get("error", "Unknown Slack error")
                raise TokenExchangeError(f"Slack error: {error_msg}")

            logger.info("Successfully exchanged Slack authorization code for token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "Bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack token exchange failed: {str(e)}")
            raise TokenExchangeError(f"Failed to exchange Slack code: {str(e)}") from e

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh Slack access token using refresh token.

        Args:
            refresh_token: Slack refresh token

        Returns:
            Dict with new access_token, refresh_token, and expires_in

        Raises:
            TokenRefreshError: If refresh fails
        """
        try:
            response = requests.post(
                "https://slack.com/api/oauth.v2.access",
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
            if not token_data.get("ok"):
                error_msg = token_data.get("error", "Unknown Slack error")
                raise TokenRefreshError(f"Slack error: {error_msg}")

            logger.info("Successfully refreshed Slack access token")

            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", refresh_token),
                "expires_in": token_data.get("expires_in", 3600),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack token refresh failed: {str(e)}")
            raise TokenRefreshError(f"Failed to refresh Slack token: {str(e)}") from e

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from Slack.

        Args:
            access_token: Valid Slack access token

        Returns:
            Dict with user data: id, name, real_name, email, team_id, etc.

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            # First get user identity
            response = requests.get(
                "https://slack.com/api/auth.test",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30,
            )

            response.raise_for_status()
            auth_data = response.json()

            if not auth_data.get("ok"):
                error_msg = auth_data.get("error", "Unknown Slack error")
                raise ProviderAPIError(f"Slack auth.test error: {error_msg}")

            user_id = auth_data["user_id"]
            team_id = auth_data["team_id"]

            # Get detailed user info
            response = requests.get(
                "https://slack.com/api/users.info",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "user": user_id,
                },
                timeout=30,
            )

            response.raise_for_status()
            user_data = response.json()

            if not user_data.get("ok"):
                error_msg = user_data.get("error", "Unknown Slack error")
                raise ProviderAPIError(f"Slack users.info error: {error_msg}")

            user = user_data["user"]

            return {
                "id": user["id"],
                "name": user["name"],
                "real_name": user.get("real_name", ""),
                "display_name": user.get("profile", {}).get("display_name", ""),
                "email": user.get("profile", {}).get("email", ""),
                "team_id": team_id,
                "is_admin": user.get("is_admin", False),
                "is_owner": user.get("is_owner", False),
                "tz": user.get("tz", ""),
                "tz_label": user.get("tz_label", ""),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack get_user_info failed: {str(e)}")
            raise ProviderAPIError(f"Failed to get Slack user info: {str(e)}") from e

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Slack access token.

        Args:
            token: Access token to revoke

        Returns:
            bool: True if revocation successful, False otherwise
        """
        try:
            response = requests.post(
                "https://slack.com/api/auth.revoke",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "test": "true",  # Test mode - doesn't actually revoke
                },
                timeout=30,
            )

            response.raise_for_status()
            revoke_data = response.json()

            # Slack returns ok: true for successful revocation
            if revoke_data.get("ok"):
                logger.info("Successfully revoked Slack token")
                return True
            else:
                error_msg = revoke_data.get("error", "Unknown Slack error")
                logger.warning(f"Slack token revocation failed: {error_msg}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack token revocation failed: {str(e)}")
            return False

    def validate_token(self, access_token: str) -> Dict:
        """
        Validate a Slack access token.

        Args:
            access_token: Token to validate

        Returns:
            Dict with token validation info

        Raises:
            ProviderAPIError: If validation fails
        """
        try:
            response = requests.get(
                "https://slack.com/api/auth.test",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30,
            )

            response.raise_for_status()
            auth_data = response.json()

            if not auth_data.get("ok"):
                error_msg = auth_data.get("error", "Unknown Slack error")
                raise ProviderAPIError(f"Slack token validation error: {error_msg}")

            return {
                "ok": True,
                "user_id": auth_data.get("user_id"),
                "team_id": auth_data.get("team_id"),
                "bot_id": auth_data.get("bot_id"),
                "is_enterprise_install": auth_data.get("is_enterprise_install", False),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Slack token validation failed: {str(e)}")
            raise ProviderAPIError(f"Failed to validate Slack token: {str(e)}") from e
