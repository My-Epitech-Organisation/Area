"""GitHub OAuth2 provider implementation."""

import logging
from typing import Dict
from urllib.parse import urlencode

import requests

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError

logger = logging.getLogger(__name__)


class GitHubOAuthProvider(BaseOAuthProvider):
    """
    GitHub OAuth2 provider implementation.

    Note: GitHub does NOT support refresh tokens. Access tokens are long-lived
    (they don't expire unless revoked), so we set a far-future expiration date.

    Scopes typically used:
        - user: Read user profile data
        - repo: Access repositories
        - notifications: Access notifications
        - read:org: Read organization membership
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate GitHub OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to GitHub
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            # Allow user to select which account to use
            "allow_signup": "true",
        }

        query_string = urlencode(params)
        authorization_url = f"{self.authorization_endpoint}?{query_string}"

        logger.info(f"Generated GitHub authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange GitHub authorization code for access token.

        Args:
            code: Authorization code from callback

        Returns:
            Dict with access_token, refresh_token (empty), expires_in, token_type

        Raises:
            TokenExchangeError: If token exchange fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
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
                raise TokenExchangeError(f"GitHub error: {error_msg}")

            logger.info("Successfully exchanged GitHub authorization code for token")

            # GitHub tokens don't expire officially, set 1 year
            return {
                "access_token": token_data["access_token"],
                "refresh_token": "",  # GitHub doesn't provide refresh tokens
                "expires_in": 31536000,  # 1 year in seconds
                "token_type": token_data.get("token_type", "bearer"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub token exchange failed: {str(e)}")
            raise TokenExchangeError(f"Failed to exchange GitHub code: {str(e)}") from e

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        GitHub does not support token refresh.

        Args:
            refresh_token: Not used

        Raises:
            NotImplementedError: Always, as GitHub doesn't support refresh
        """
        raise NotImplementedError(
            "GitHub does not support refresh tokens. "
            "Access tokens are long-lived and don't expire."
        )

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from GitHub.

        Args:
            access_token: Valid GitHub access token

        Returns:
            Dict with login, email, name, avatar_url, etc.

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            response = requests.get(
                self.userinfo_endpoint or "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            # GitHub may not expose email in /user if it's private
            # We need to fetch emails separately if needed
            email = data.get("email")
            if not email:
                email = self._get_primary_email(access_token)

            return {
                "login": data.get("login"),
                "email": email,
                "name": data.get("name"),
                "avatar_url": data.get("avatar_url"),
                "bio": data.get("bio"),
                "company": data.get("company"),
                "location": data.get("location"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch GitHub user info: {str(e)}")
            raise ProviderAPIError(f"Failed to get GitHub user info: {str(e)}") from e

    def _get_primary_email(self, access_token: str) -> str:
        """
        Fetch user's primary email from GitHub emails endpoint.

        Args:
            access_token: Valid GitHub access token

        Returns:
            str: Primary email address or empty string
        """
        try:
            response = requests.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=30,
            )

            response.raise_for_status()
            emails = response.json()

            # Find primary email
            for email_data in emails:
                if email_data.get("primary") and email_data.get("verified"):
                    return email_data.get("email", "")

            # Fallback to first verified email
            for email_data in emails:
                if email_data.get("verified"):
                    return email_data.get("email", "")

            return ""

        except Exception as e:
            logger.warning(f"Failed to fetch GitHub emails: {str(e)}")
            return ""

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a GitHub access token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # GitHub requires Basic Auth with client_id:client_secret
            response = requests.delete(
                f"https://api.github.com/applications/{self.client_id}/token",
                auth=(self.client_id, self.client_secret),
                json={"access_token": token},
                timeout=30,
            )

            success = response.status_code == 204
            if success:
                logger.info("Successfully revoked GitHub token")
            else:
                logger.warning(
                    f"GitHub token revocation returned {response.status_code}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to revoke GitHub token: {str(e)}")
            return False
