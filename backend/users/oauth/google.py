"""Google OAuth2 provider implementation."""

import logging
from typing import Dict

import requests
from authlib.integrations.requests_client import OAuth2Session

from .base import BaseOAuthProvider
from .exceptions import ProviderAPIError, TokenExchangeError, TokenRefreshError

logger = logging.getLogger(__name__)


class GoogleOAuthProvider(BaseOAuthProvider):
    """
    Google OAuth2 provider implementation.

    Supports OpenID Connect with refresh tokens for long-lived access.
    Provides access to Gmail, Google Calendar, Drive, and other Google services.

    Scopes typically used:
        - openid: OpenID Connect authentication
        - email: Access to user's email address
        - profile: Access to user's basic profile
        - https://www.googleapis.com/auth/gmail.readonly: Read Gmail messages
    """

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth2 authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            str: Full authorization URL to redirect user to Google
        """
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=" ".join(self.scopes),
            state=state,
        )

        authorization_url, _ = oauth.create_authorization_url(
            self.authorization_endpoint,
            # Request offline access to get refresh token
            access_type="offline",
            # Force consent screen to always get refresh token
            prompt="consent",
        )

        logger.info(f"Generated Google authorization URL with state={state}")
        return authorization_url

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange Google authorization code for tokens.

        Args:
            code: Authorization code from callback

        Returns:
            Dict with access_token, refresh_token, expires_in, token_type

        Raises:
            TokenExchangeError: If token exchange fails
        """
        try:
            oauth = OAuth2Session(
                client_id=self.client_id, redirect_uri=self.redirect_uri
            )

            token = oauth.fetch_token(
                url=self.token_endpoint,
                code=code,
                client_secret=self.client_secret,
            )

            logger.info("Successfully exchanged Google authorization code for token")

            return {
                "access_token": token["access_token"],
                "refresh_token": token.get("refresh_token", ""),
                "expires_in": token.get("expires_in", 3600),
                "token_type": token.get("token_type", "Bearer"),
            }

        except Exception as e:
            logger.error(f"Google token exchange failed: {str(e)}")
            raise TokenExchangeError(f"Failed to exchange Google code: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh Google access token using refresh token.

        Args:
            refresh_token: Google refresh token

        Returns:
            Dict with new access_token and expires_in

        Raises:
            TokenRefreshError: If refresh fails
        """
        try:
            response = requests.post(
                self.token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            response.raise_for_status()
            token = response.json()

            logger.info("Successfully refreshed Google access token")

            return {
                "access_token": token["access_token"],
                "expires_in": token.get("expires_in", 3600),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Google token refresh failed: {str(e)}")
            raise TokenRefreshError(f"Failed to refresh Google token: {str(e)}")

    def get_user_info(self, access_token: str) -> Dict:
        """
        Fetch user information from Google.

        Args:
            access_token: Valid Google access token

        Returns:
            Dict with email, name, picture, verified_email

        Raises:
            ProviderAPIError: If API call fails
        """
        try:
            response = requests.get(
                self.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            response.raise_for_status()
            data = response.json()

            return {
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture"),
                "verified_email": data.get("verified_email", False),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Google user info: {str(e)}")
            raise ProviderAPIError(f"Failed to get Google user info: {str(e)}")

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a Google access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                "https://oauth2.googleapis.com/revoke",
                data={"token": token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            success = response.status_code == 200
            if success:
                logger.info("Successfully revoked Google token")
            else:
                logger.warning(f"Google token revocation returned {response.status_code}")

            return success

        except Exception as e:
            logger.error(f"Failed to revoke Google token: {str(e)}")
            return False
