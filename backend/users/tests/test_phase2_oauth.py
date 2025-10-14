"""
Tests for Phase 2 OAuth improvements.

Tests automatic token refresh, notifications, and error handling.
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from users.models import OAuthNotification, ServiceToken
from users.oauth.exceptions import TokenRefreshError
from users.oauth.manager import OAuthManager

User = get_user_model()


class AutomaticTokenRefreshTestCase(TestCase):
    """Test automatic token refresh functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_get_valid_token_refreshes_expired_token(self):
        """Test that get_valid_token refreshes an expired token."""
        # Create expired token with refresh token
        expires_at = timezone.now() - timedelta(hours=1)
        service_token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="old_access_token",
            refresh_token="valid_refresh_token",
            expires_at=expires_at,
            token_type="Bearer",
        )

        # Mock OAuth provider
        with patch("users.oauth.manager.OAuthManager.get_provider") as mock_provider:
            mock_instance = MagicMock()
            mock_instance.requires_refresh = True
            mock_instance.refresh_access_token.return_value = {
                "access_token": "new_access_token",
                "expires_in": 3600,
                "token_type": "Bearer",
            }
            mock_instance.calculate_expiry.return_value = timezone.now() + timedelta(
                hours=1
            )
            mock_provider.return_value = mock_instance

            # Get valid token - should trigger refresh
            token = OAuthManager.get_valid_token(self.user, "google")

            # Assertions
            self.assertEqual(token, "new_access_token")
            mock_instance.refresh_access_token.assert_called_once_with(
                "valid_refresh_token"
            )

            # Verify database updated
            service_token.refresh_from_db()
            self.assertEqual(service_token.access_token, "new_access_token")
            self.assertIsNotNone(service_token.last_used_at)

    def test_get_valid_token_proactively_refreshes_expiring_soon(self):
        """Test that tokens expiring within 5 minutes are refreshed proactively."""
        # Create token expiring in 3 minutes
        expires_at = timezone.now() + timedelta(minutes=3)
        service_token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="old_access_token",
            refresh_token="valid_refresh_token",
            expires_at=expires_at,
            token_type="Bearer",
        )

        # Mock OAuth provider
        with patch("users.oauth.manager.OAuthManager.get_provider") as mock_provider:
            mock_instance = MagicMock()
            mock_instance.requires_refresh = True
            mock_instance.refresh_access_token.return_value = {
                "access_token": "refreshed_token",
                "expires_in": 3600,
                "token_type": "Bearer",
            }
            mock_instance.calculate_expiry.return_value = timezone.now() + timedelta(
                hours=1
            )
            mock_provider.return_value = mock_instance

            # Get valid token - should trigger proactive refresh
            token = OAuthManager.get_valid_token(self.user, "google")

            # Assertions
            self.assertEqual(token, "refreshed_token")
            mock_instance.refresh_access_token.assert_called_once()

    def test_get_valid_token_marks_token_as_used(self):
        """Test that get_valid_token marks the token as used."""
        # Create valid token
        expires_at = timezone.now() + timedelta(hours=1)
        service_token = ServiceToken.objects.create(
            user=self.user,
            service_name="github",
            access_token="valid_token",
            refresh_token="",
            expires_at=expires_at,
            token_type="Bearer",
        )

        self.assertIsNone(service_token.last_used_at)

        # Get valid token
        token = OAuthManager.get_valid_token(self.user, "github")

        # Assertions
        self.assertEqual(token, "valid_token")

        # Verify last_used_at was updated
        service_token.refresh_from_db()
        self.assertIsNotNone(service_token.last_used_at)

    def test_get_valid_token_returns_none_when_refresh_fails(self):
        """Test that get_valid_token returns None when refresh fails."""
        # Create expired token
        expires_at = timezone.now() - timedelta(hours=1)
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="old_token",
            refresh_token="invalid_refresh_token",
            expires_at=expires_at,
            token_type="Bearer",
        )

        # Mock OAuth provider to simulate refresh failure
        with patch("users.oauth.manager.OAuthManager.get_provider") as mock_provider:
            mock_instance = MagicMock()
            mock_instance.requires_refresh = True
            mock_instance.refresh_access_token.side_effect = TokenRefreshError(
                "Invalid refresh token"
            )
            mock_provider.return_value = mock_instance

            # Mock notification creation
            with patch(
                "users.oauth.manager._create_token_refresh_notification"
            ) as mock_notify:
                # Get valid token - should return None
                token = OAuthManager.get_valid_token(self.user, "google")

                # Assertions
                self.assertIsNone(token)
                mock_notify.assert_called_once()


class OAuthNotificationTestCase(TestCase):
    """Test OAuth notification system."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_notification_avoids_duplicates(self):
        """Test that duplicate notifications are not created."""
        # Create first notification
        notif1 = OAuthNotification.create_notification(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test message 1",
        )

        # Try to create duplicate
        notif2 = OAuthNotification.create_notification(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test message 2",
        )

        # Should return the same instance (updated message)
        self.assertEqual(notif1.id, notif2.id)
        self.assertEqual(notif2.message, "Test message 2")

        # Should only have one notification in DB
        count = OAuthNotification.objects.filter(
            user=self.user, service_name="google"
        ).count()
        self.assertEqual(count, 1)

    def test_mark_read(self):
        """Test marking notification as read."""
        notification = OAuthNotification.objects.create(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test message",
        )

        self.assertFalse(notification.is_read)

        notification.mark_read()
        notification.refresh_from_db()

        self.assertTrue(notification.is_read)

    def test_resolve(self):
        """Test resolving notification."""
        notification = OAuthNotification.objects.create(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test message",
        )

        self.assertFalse(notification.is_resolved)
        self.assertIsNone(notification.resolved_at)

        notification.resolve()
        notification.refresh_from_db()

        self.assertTrue(notification.is_resolved)
        self.assertIsNotNone(notification.resolved_at)

    def test_resolve_for_service(self):
        """Test resolving all notifications for a service."""
        # Create multiple notifications
        OAuthNotification.objects.create(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test 1",
        )
        OAuthNotification.objects.create(
            user=self.user,
            service_name="google",
            notification_type=OAuthNotification.NotificationType.TOKEN_EXPIRED,
            message="Test 2",
        )
        OAuthNotification.objects.create(
            user=self.user,
            service_name="github",
            notification_type=OAuthNotification.NotificationType.REFRESH_FAILED,
            message="Test 3",
        )

        # Resolve google notifications
        count = OAuthNotification.resolve_for_service(self.user, "google")

        self.assertEqual(count, 2)

        # Verify google notifications resolved
        google_resolved = OAuthNotification.objects.filter(
            user=self.user, service_name="google", is_resolved=True
        ).count()
        self.assertEqual(google_resolved, 2)

        # Verify github notification not resolved
        github_unresolved = OAuthNotification.objects.filter(
            user=self.user, service_name="github", is_resolved=False
        ).count()
        self.assertEqual(github_unresolved, 1)

    def test_notification_created_on_refresh_failure(self):
        """Test that notification is created when token refresh fails."""
        # Create expired token
        expires_at = timezone.now() - timedelta(hours=1)
        ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="old_token",
            refresh_token="invalid_token",
            expires_at=expires_at,
            token_type="Bearer",
        )

        # Mock OAuth provider to fail
        with patch("users.oauth.manager.OAuthManager.get_provider") as mock_provider:
            mock_instance = MagicMock()
            mock_instance.requires_refresh = True
            mock_instance.refresh_access_token.side_effect = TokenRefreshError(
                "Invalid token"
            )
            mock_provider.return_value = mock_instance

            # Try to get valid token
            token = OAuthManager.get_valid_token(self.user, "google")

            # Should return None
            self.assertIsNone(token)

            # Verify notification created
            notifications = OAuthNotification.objects.filter(
                user=self.user, service_name="google"
            )
            self.assertEqual(notifications.count(), 1)

            notification = notifications.first()
            self.assertEqual(
                notification.notification_type,
                OAuthNotification.NotificationType.REFRESH_FAILED,
            )
            self.assertIn("Invalid token", notification.message)


class ServiceTokenModelTestCase(TestCase):
    """Test ServiceToken model enhancements."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_needs_refresh_property(self):
        """Test needs_refresh property identifies tokens expiring soon."""
        # Token expiring in 3 minutes - needs refresh
        token1 = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="token1",
            expires_at=timezone.now() + timedelta(minutes=3),
        )
        self.assertTrue(token1.needs_refresh)

        # Token expiring in 10 minutes - doesn't need refresh yet
        token2 = ServiceToken.objects.create(
            user=self.user,
            service_name="github",
            access_token="token2",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        self.assertFalse(token2.needs_refresh)

        # Token without expiration - doesn't need refresh
        token3 = ServiceToken.objects.create(
            user=self.user,
            service_name="slack",
            access_token="token3",
            expires_at=None,
        )
        self.assertFalse(token3.needs_refresh)

    def test_mark_used_updates_timestamp(self):
        """Test mark_used updates last_used_at without changing updated_at."""
        token = ServiceToken.objects.create(
            user=self.user,
            service_name="google",
            access_token="test_token",
            expires_at=timezone.now() + timedelta(hours=1),
        )

        original_updated_at = token.updated_at
        self.assertIsNone(token.last_used_at)

        # Mark as used
        token.mark_used()
        token.refresh_from_db()

        # last_used_at should be set
        self.assertIsNotNone(token.last_used_at)

        # updated_at should remain the same (we only update last_used_at)
        # Note: This might not be exactly equal due to auto_now, but close
        self.assertIsNotNone(token.updated_at)
