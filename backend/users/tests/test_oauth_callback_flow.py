"""
Tests for OAuth2 callback flow (Backend-First implementation).

This module tests the refactored OAuth2 callback flow where all token
handling is done server-side for security.
"""

from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from users.models import ServiceToken
from users.oauth.exceptions import OAuthError, OAuthStateError

User = get_user_model()


class OAuthCallbackBackendFirstTestCase(TestCase):
    """Test the Backend-First OAuth callback flow."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @patch("users.oauth_views.OAuthManager")
    @patch("users.oauth_views.settings")
    def test_successful_oauth_callback(self, mock_settings, mock_manager):
        """Test successful OAuth callback with valid state and code."""
        # Setup
        mock_settings.FRONTEND_URL = "http://localhost:5173"

        # Mock state validation
        mock_manager.validate_state.return_value = (True, None)

        # Mock provider
        mock_provider = Mock()
        mock_provider.exchange_code_for_token.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_provider.calculate_expiry.return_value = timezone.now() + timedelta(
            hours=1
        )
        mock_provider.scopes = ["email", "profile"]
        mock_manager.get_provider.return_value = mock_provider

        # Mock cache for state data
        with patch("django.core.cache.cache") as mock_cache:
            mock_cache.get.return_value = {"user_id": str(self.user.id), "provider": "google"}

            response = self.client.get(
                "/auth/oauth/google/callback/",
                {"code": "test_code", "state": "test_state"},
            )

            # Should redirect to frontend with success
            self.assertEqual(response.status_code, 302)
            location = response.headers["Location"]
            self.assertIn("http://localhost:5173/auth/callback/google", location)
            self.assertIn("success=true", location)
            self.assertIn("service=google", location)

            # Verify token was created
            token = ServiceToken.objects.get(user=self.user, service_name="google")
            self.assertEqual(token.access_token, "test_access_token")
            self.assertEqual(token.refresh_token, "test_refresh_token")
            self.assertEqual(token.token_type, "Bearer")
            self.assertEqual(token.scopes, "email profile")

    @patch("users.oauth_views.settings")
    def test_oauth_callback_invalid_state(self, mock_settings):
        """Test OAuth callback with invalid/expired state."""
        mock_settings.FRONTEND_URL = "http://localhost:5173"

        # Mock cache returns None (expired state)
        with patch("django.core.cache.cache") as mock_cache:
            mock_cache.get.return_value = None

            response = self.client.get(
                "/auth/oauth/google/callback/",
                {"code": "test_code", "state": "invalid_state"},
            )

            # Should redirect to frontend with error
            self.assertEqual(response.status_code, 302)
            location = response.headers["Location"]
            self.assertIn("http://localhost:5173/auth/callback/google", location)
            self.assertIn("error=invalid_state", location)

    @patch("users.oauth_views.settings")
    def test_oauth_callback_provider_error(self, mock_settings):
        """Test OAuth callback when provider returns error."""
        mock_settings.FRONTEND_URL = "http://localhost:5173"

        response = self.client.get(
            "/auth/oauth/google/callback/",
            {"error": "access_denied", "error_description": "User denied access"},
        )

        # Should redirect to frontend with provider error
        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        self.assertIn("http://localhost:5173/auth/callback/google", location)
        self.assertIn("error=access_denied", location)
        self.assertIn("message=User+denied+access", location)

    @patch("users.oauth_views.OAuthManager")
    @patch("users.oauth_views.settings")
    def test_oauth_callback_token_exchange_error(self, mock_settings, mock_manager):
        """Test OAuth callback when token exchange fails."""
        mock_settings.FRONTEND_URL = "http://localhost:5173"

        # Mock state validation
        mock_manager.validate_state.return_value = (True, None)

        # Mock provider to raise error on token exchange
        mock_provider = Mock()
        mock_provider.exchange_code_for_token.side_effect = OAuthError(
            "Failed to exchange token"
        )
        mock_manager.get_provider.return_value = mock_provider

        # Mock cache for state data
        with patch("django.core.cache.cache") as mock_cache:
            mock_cache.get.return_value = {"user_id": str(self.user.id), "provider": "google"}

            response = self.client.get(
                "/auth/oauth/google/callback/",
                {"code": "test_code", "state": "test_state"},
            )

            # Should redirect to frontend with oauth_error
            self.assertEqual(response.status_code, 302)
            location = response.headers["Location"]
            self.assertIn("http://localhost:5173/auth/callback/google", location)
            self.assertIn("error=oauth_error", location)

    @patch("users.oauth_views.OAuthManager")
    @patch("users.oauth_views.settings")
    def test_oauth_callback_reconnect_existing_service(self, mock_settings, mock_manager):
        """Test OAuth callback when service is already connected (reconnect)."""
        # Create existing token
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="old_token",
            refresh_token="old_refresh",
        )

        mock_settings.FRONTEND_URL = "http://localhost:5173"

        # Mock state validation
        mock_manager.validate_state.return_value = (True, None)

        # Mock provider
        mock_provider = Mock()
        mock_provider.exchange_code_for_token.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_provider.calculate_expiry.return_value = timezone.now() + timedelta(
            hours=1
        )
        mock_provider.scopes = ["email", "profile"]
        mock_manager.get_provider.return_value = mock_provider

        # Mock cache for state data
        with patch("django.core.cache.cache") as mock_cache:
            mock_cache.get.return_value = {"user_id": str(self.user.id), "provider": "google"}

            response = self.client.get(
                "/auth/oauth/google/callback/",
                {"code": "test_code", "state": "test_state"},
            )

            # Should redirect with created=false
            self.assertEqual(response.status_code, 302)
            location = response.headers["Location"]
            self.assertIn("created=false", location)

            # Verify token was updated
            token = ServiceToken.objects.get(user=self.user, service_name="google")
            self.assertEqual(token.access_token, "new_access_token")
            self.assertEqual(token.refresh_token, "new_refresh_token")


class ServiceTokenModelTestCase(TestCase):
    """Test enhanced ServiceToken model features."""

    def setUp(self):
        """Set up test user and token."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_is_expired_property_not_expired(self):
        """Test is_expired returns False for valid token."""
        future_expiry = timezone.now() + timedelta(hours=1)
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=future_expiry,
        )

        self.assertFalse(token.is_expired)

    def test_is_expired_property_expired(self):
        """Test is_expired returns True for expired token."""
        past_expiry = timezone.now() - timedelta(hours=1)
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=past_expiry,
        )

        self.assertTrue(token.is_expired)

    def test_is_expired_property_never_expires(self):
        """Test is_expired returns False when expires_at is None."""
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="github",
            access_token="test_token",
            expires_at=None,
        )

        self.assertFalse(token.is_expired)

    def test_needs_refresh_property_yes(self):
        """Test needs_refresh returns True when token expires soon."""
        soon_expiry = timezone.now() + timedelta(minutes=3)
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=soon_expiry,
        )

        self.assertTrue(token.needs_refresh)

    def test_needs_refresh_property_no(self):
        """Test needs_refresh returns False when token expires later."""
        later_expiry = timezone.now() + timedelta(hours=1)
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=later_expiry,
        )

        self.assertFalse(token.needs_refresh)

    def test_mark_used_updates_last_used_at(self):
        """Test mark_used updates last_used_at timestamp."""
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
        )

        self.assertIsNone(token.last_used_at)

        token.mark_used()
        token.refresh_from_db()

        self.assertIsNotNone(token.last_used_at)
        self.assertLess(
            (timezone.now() - token.last_used_at).total_seconds(), 1
        )  # Within 1 second

    def test_scopes_list_methods(self):
        """Test get_scopes_list and set_scopes_list methods."""
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
        )

        # Set scopes
        scopes = ["email", "profile", "openid"]
        token.set_scopes_list(scopes)
        token.save()

        # Get scopes
        token.refresh_from_db()
        retrieved_scopes = token.get_scopes_list()

        self.assertEqual(retrieved_scopes, scopes)
        self.assertEqual(token.scopes, "email profile openid")

    def test_time_until_expiry(self):
        """Test time_until_expiry calculation."""
        future_expiry = timezone.now() + timedelta(hours=2)
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=future_expiry,
        )

        time_left = token.time_until_expiry
        self.assertIsNotNone(time_left)
        # Should be approximately 2 hours (with small tolerance)
        self.assertAlmostEqual(time_left.total_seconds(), 7200, delta=2)

    def test_string_representation(self):
        """Test __str__ method."""
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
        )

        expected = f"{self.user.email} - google (valid)"
        self.assertEqual(str(token), expected)

        # Test with expired token
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        expected_expired = f"{self.user.email} - google (expired)"
        self.assertEqual(str(token), expected_expired)
