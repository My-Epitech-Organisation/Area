"""Tests for password reset functionality."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from ..models import PasswordResetToken

User = get_user_model()


class PasswordResetTokenModelTest(TestCase):
    """Test PasswordResetToken model."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_token_generation(self):
        """Test that token is auto-generated."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        self.assertIsNotNone(reset_token.token)
        self.assertEqual(len(reset_token.token), 64)

    def test_token_expiration_set(self):
        """Test that expiration is auto-set."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        self.assertIsNotNone(reset_token.expires_at)
        self.assertGreater(reset_token.expires_at, timezone.now())

    def test_is_valid_unused_token(self):
        """Test that unused, unexpired token is valid."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        self.assertTrue(reset_token.is_valid())

    def test_is_valid_used_token(self):
        """Test that used token is invalid."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        reset_token.mark_used()
        self.assertFalse(reset_token.is_valid())

    def test_is_valid_expired_token(self):
        """Test that expired token is invalid."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        # Manually set expiration to past
        reset_token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        reset_token.save()
        self.assertFalse(reset_token.is_valid())

    def test_mark_used(self):
        """Test marking token as used."""
        reset_token = PasswordResetToken.objects.create(user=self.user)
        self.assertFalse(reset_token.used)
        reset_token.mark_used()
        self.assertTrue(reset_token.used)


class ForgotPasswordViewTest(APITestCase):
    """Test forgot password endpoint."""

    def setUp(self):
        """Set up test users."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.url = "/auth/forgot-password/"

    @patch("users.password_views.send_mail")
    def test_forgot_password_existing_user(self, mock_send_mail):
        """Test requesting password reset for existing user."""
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("If an account exists", response.data["message"])

        # Check that token was created
        self.assertTrue(
            PasswordResetToken.objects.filter(user=self.user, used=False).exists()
        )

        # Check that email was sent
        mock_send_mail.assert_called_once()

    @patch("users.password_views.send_mail")
    def test_forgot_password_nonexistent_user(self, mock_send_mail):
        """Test requesting password reset for non-existent user."""
        data = {"email": "nonexistent@example.com"}
        response = self.client.post(self.url, data, format="json")

        # Should still return success to prevent user enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("If an account exists", response.data["message"])

        # No email should be sent
        mock_send_mail.assert_not_called()

    @patch("users.password_views.send_mail")
    def test_forgot_password_invalidates_old_tokens(self, mock_send_mail):
        """Test that requesting reset invalidates old tokens."""
        # Create old token
        old_token = PasswordResetToken.objects.create(user=self.user)
        old_token_value = old_token.token

        # Request new reset
        data = {"email": "test@example.com"}
        self.client.post(self.url, data, format="json")

        # Old token should be marked as used
        old_token.refresh_from_db()
        self.assertTrue(old_token.used)

        # New token should exist
        new_token = PasswordResetToken.objects.filter(
            user=self.user, used=False
        ).first()
        self.assertIsNotNone(new_token)
        self.assertNotEqual(new_token.token, old_token_value)

    def test_forgot_password_missing_email(self):
        """Test forgot password with missing email."""
        data = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forgot_password_invalid_email(self):
        """Test forgot password with invalid email format."""
        data = {"email": "not-an-email"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordViewTest(APITestCase):
    """Test reset password endpoint."""

    def setUp(self):
        """Set up test user and token."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )
        self.reset_token = PasswordResetToken.objects.create(user=self.user)
        self.url = "/auth/reset-password/"

    def test_reset_password_success(self):
        """Test successful password reset."""
        data = {
            "token": self.reset_token.token,
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("successfully", response.data["message"])

        # Check that password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

        # Check that token was marked as used
        self.reset_token.refresh_from_db()
        self.assertTrue(self.reset_token.used)

    def test_reset_password_invalid_token(self):
        """Test reset with invalid token."""
        data = {
            "token": "invalid-token-12345",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_expired_token(self):
        """Test reset with expired token."""
        # Expire the token
        self.reset_token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        self.reset_token.save()

        data = {
            "token": self.reset_token.token,
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_used_token(self):
        """Test reset with already used token."""
        self.reset_token.mark_used()

        data = {
            "token": self.reset_token.token,
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_mismatch(self):
        """Test reset with mismatched passwords."""
        data = {
            "token": self.reset_token.token,
            "new_password": "newpass123",
            "confirm_password": "different123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_too_short(self):
        """Test reset with password too short."""
        data = {
            "token": self.reset_token.token,
            "new_password": "short",
            "confirm_password": "short",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordViewTest(APITestCase):
    """Test change password endpoint."""

    def setUp(self):
        """Set up authenticated user."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/auth/change-password/"

    def test_change_password_success(self):
        """Test successful password change."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("successfully", response.data["message"])

        # Check that password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_change_password_wrong_old_password(self):
        """Test change password with wrong old password."""
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test change password with mismatched new passwords."""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "confirm_password": "different123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """Test that unauthenticated users cannot change password."""
        self.client.force_authenticate(user=None)
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
