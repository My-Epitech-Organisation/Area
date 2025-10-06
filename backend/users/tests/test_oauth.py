"""
Tests for OAuth2 integration.

This module contains tests for:
- OAuth2 providers (Google, GitHub)
- OAuth2 manager
- OAuth2 views and flow
- Token validation and refresh
"""

from datetime import timedelta
from unittest.mock import MagicMock, Mock, patch

from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from users.models import ServiceToken
from users.oauth.exceptions import InvalidProviderError, TokenExchangeError
from users.oauth.google import GoogleOAuthProvider
from users.oauth.manager import OAuthManager

User = get_user_model()


class OAuthManagerTestCase(TestCase):
    """Test OAuth2 Manager functionality."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @patch("users.oauth.manager.settings")
    def test_get_provider_google(self, mock_settings):
        """Test getting Google provider."""
        mock_settings.OAUTH2_PROVIDERS = {
            "google": {
                "client_id": "test_client_id",
                "client_secret": "test_secret",
                "redirect_uri": "http://localhost/callback",
                "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_endpoint": "https://oauth2.googleapis.com/token",
                "scopes": ["email", "profile"],
            }
        }

        provider = OAuthManager.get_provider("google")
        self.assertIsInstance(provider, GoogleOAuthProvider)
        self.assertEqual(provider.client_id, "test_client_id")

    def test_get_provider_invalid(self):
        """Test getting invalid provider raises error."""
        with self.assertRaises(InvalidProviderError):
            OAuthManager.get_provider("invalid_provider")

    def test_get_valid_token_not_exists(self):
        """Test getting token when none exists."""
        token = OAuthManager.get_valid_token(self.user, "google")
        self.assertIsNone(token)

    def test_get_valid_token_not_expired(self):
        """Test getting valid token that hasn't expired."""
        # Create a non-expired token
        future_expiry = timezone.now() + timedelta(hours=1)
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="valid_token_123",
            refresh_token="refresh_token_123",
            expires_at=future_expiry,
        )

        token = OAuthManager.get_valid_token(self.user, "google")
        self.assertEqual(token, "valid_token_123")

    def test_get_valid_token_expired_no_refresh(self):
        """Test getting expired token without refresh token."""
        # Create an expired token without refresh token
        past_expiry = timezone.now() - timedelta(hours=1)
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="expired_token_123",
            refresh_token="",
            expires_at=past_expiry,
        )

        token = OAuthManager.get_valid_token(self.user, "google")
        self.assertIsNone(token)

    def test_generate_and_validate_state(self):
        """Test state generation and validation."""
        state = OAuthManager.generate_state(str(self.user.id), "google")
        self.assertIsNotNone(state)
        self.assertGreater(len(state), 20)  # Should be a long random string

        # Validate the state
        is_valid, error = OAuthManager.validate_state(
            state, str(self.user.id), "google"
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_state_invalid(self):
        """Test validating invalid state."""
        is_valid, error = OAuthManager.validate_state(
            "invalid_state", str(self.user.id), "google"
        )
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_revoke_user_token(self):
        """Test revoking a user's token."""
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="token_to_revoke",
            refresh_token="",
        )

        # Revoke the token
        result = OAuthManager.revoke_user_token(self.user, "google")
        self.assertTrue(result)

        # Verify token is deleted
        exists = ServiceToken.objects.filter(
            user=self.user, service_name="google"
        ).exists()
        self.assertFalse(exists)


class OAuthViewsTestCase(APITestCase):
    """Test OAuth2 API views."""

    def setUp(self):
        """Set up test user and authenticate."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    @patch("users.oauth_views.OAuthManager")
    @patch("users.oauth_views.settings")
    def test_oauth_initiate_google(self, mock_settings, mock_manager):
        """Test initiating OAuth2 flow for Google."""
        mock_settings.OAUTH2_PROVIDERS = {"google": {"client_id": "test"}}
        mock_manager.is_provider_available.return_value = True
        mock_manager.generate_state.return_value = "test_state_123"

        # Create mock provider
        mock_provider = Mock()
        mock_provider.get_authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/v2/auth?client_id=test&state=test_state_123"
        )
        mock_manager.get_provider.return_value = mock_provider

        response = self.client.get("/auth/oauth/google/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("redirect_url", response.data)
        self.assertIn("state", response.data)
        self.assertEqual(response.data["provider"], "google")

    def test_oauth_initiate_invalid_provider(self):
        """Test initiating OAuth2 with invalid provider."""
        response = self.client.get("/auth/oauth/invalid_provider/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_service_list(self):
        """Test listing connected services."""
        # Create some connected services
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="token_1",
        )
        ServiceToken.objects.create(
            user=self.user,
            service_name="github",
            access_token="token_2",
        )

        response = self.client.get("/auth/services/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["connected_services"]), 2)
        self.assertIn("available_providers", response.data)
        self.assertEqual(response.data["total_connected"], 2)

    def test_service_disconnect(self):
        """Test disconnecting a service."""
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="token_to_disconnect",
        )

        response = self.client.delete("/auth/services/google/disconnect/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

        # Verify token is deleted
        exists = ServiceToken.objects.filter(
            user=self.user, service_name="google"
        ).exists()
        self.assertFalse(exists)

    def test_service_disconnect_not_connected(self):
        """Test disconnecting a service that's not connected."""
        response = self.client.delete("/auth/services/google/disconnect/")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)


class GoogleOAuthProviderTestCase(TestCase):
    """Test Google OAuth2 provider."""

    def setUp(self):
        """Set up provider configuration."""
        self.config = {
            "client_id": "test_client_id",
            "client_secret": "test_secret",
            "redirect_uri": "http://localhost/callback",
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_endpoint": "https://oauth2.googleapis.com/token",
            "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
            "scopes": ["email", "profile"],
            "requires_refresh": True,
        }
        self.provider = GoogleOAuthProvider(self.config)

    def test_get_authorization_url(self):
        """Test generating authorization URL."""
        state = "test_state_123"
        url = self.provider.get_authorization_url(state)

        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", url)
        self.assertIn(f"state={state}", url)
        self.assertIn("client_id=test_client_id", url)

    @patch("users.oauth.google.requests.post")
    def test_refresh_access_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.provider.refresh_access_token("refresh_token_123")

        self.assertEqual(result["access_token"], "new_access_token")
        self.assertEqual(result["expires_in"], 3600)

    def test_calculate_expiry(self):
        """Test token expiry calculation."""
        expires_in = 3600  # 1 hour
        expiry = self.provider.calculate_expiry(expires_in)

        expected_expiry = timezone.now() + timedelta(seconds=3600)
        # Allow 2 seconds tolerance for test execution time
        self.assertAlmostEqual(
            expiry.timestamp(), expected_expiry.timestamp(), delta=2
        )
