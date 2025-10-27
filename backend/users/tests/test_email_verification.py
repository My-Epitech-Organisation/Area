"""
Tests for email verification functionality.
"""

from datetime import timedelta
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from django.core import mail
from django.utils import timezone

from users.models import User


class EmailVerificationTestCase(APITestCase):
    """Test suite for email verification functionality."""

    def setUp(self):
        """Set up test data."""
        self.register_url = "/auth/register/"
        self.send_verification_url = "/auth/send-verification-email/"
        self.login_url = "/auth/login/"

    def test_user_registration_sends_verification_email(self):
        """Test that registering a user sends a verification email."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
            "username": "New User",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that user was created with email_verified=False
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(user.email_verified)
        self.assertTrue(len(user.email_verification_token) > 0)
        self.assertIsNotNone(user.email_verification_token_expires)

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify", mail.outbox[0].subject)
        self.assertIn(user.email_verification_token, mail.outbox[0].body)

    def test_email_verification_with_valid_token(self):
        """Test verifying email with a valid token."""
        # Create user with verification token
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            username="testuser",
        )
        user.email_verified = False
        user.email_verification_token = "valid_token_12345"
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save()

        # Verify email
        verify_url = f"/auth/verify-email/{user.email_verification_token}/"
        response = self.client.get(verify_url)

        # Should redirect to frontend with success parameters
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=true", location)
        self.assertIn("message=", location)
        self.assertIn("email=", location)

        # Check that user is now verified
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertEqual(user.email_verification_token, "")
        self.assertIsNone(user.email_verification_token_expires)

    def test_email_verification_with_invalid_token(self):
        """Test verifying email with an invalid token."""
        verify_url = "/auth/verify-email/invalid_token_xyz/"
        response = self.client.get(verify_url)

        # Should redirect to frontend with error parameters
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=false", location)
        self.assertIn("error=", location)

    def test_email_verification_with_expired_token(self):
        """Test verifying email with an expired token."""
        # Create user with expired token
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            username="testuser",
        )
        user.email_verified = False
        user.email_verification_token = "expired_token_12345"
        user.email_verification_token_expires = timezone.now() - timedelta(hours=1)
        user.save()

        # Try to verify email
        verify_url = f"/auth/verify-email/{user.email_verification_token}/"
        response = self.client.get(verify_url)

        # Should redirect to frontend with expired error
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=false", location)
        self.assertIn("expired=true", location)
        self.assertIn("error=", location)

        # Check that user is still not verified
        user.refresh_from_db()
        self.assertFalse(user.email_verified)

    def test_email_verification_already_verified(self):
        """Test verifying an already verified email."""
        # Create verified user
        user = User.objects.create_user(
            email="verified@example.com",
            password="testpass123",
            username="verifieduser",
        )
        user.email_verified = True
        user.email_verification_token = "some_token"
        user.save()

        # Try to verify again
        verify_url = f"/auth/verify-email/{user.email_verification_token}/"
        response = self.client.get(verify_url)

        # Should redirect to frontend with already verified message
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=true", location)
        self.assertIn("already_verified=true", location)
        self.assertIn("message=", location)

    def test_resend_verification_email(self):
        """Test resending verification email."""
        # Create unverified user
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            username="testuser",
        )
        user.email_verified = False
        user.save()

        # Login
        self.client.force_authenticate(user=user)

        # Request new verification email
        response = self.client.post(self.send_verification_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sent successfully", response.data["message"].lower())

        # Check that new token was generated
        user.refresh_from_db()
        self.assertTrue(len(user.email_verification_token) > 0)
        self.assertIsNotNone(user.email_verification_token_expires)

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_verification_email_already_verified(self):
        """Test that verified users cannot request new verification email."""
        # Create verified user
        user = User.objects.create_user(
            email="verified@example.com",
            password="testpass123",
            username="verifieduser",
        )
        user.email_verified = True
        user.save()

        # Login
        self.client.force_authenticate(user=user)

        # Try to request verification email
        response = self.client.post(self.send_verification_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already verified", response.data["message"].lower())

        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_verification_email_unauthenticated(self):
        """Test that unauthenticated users cannot request verification email."""
        response = self.client.post(self.send_verification_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_verification_html_content(self):
        """Test that verification email contains HTML content."""
        data = {
            "email": "htmltest@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that email has HTML alternative
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        # Check for HTML content
        self.assertTrue(any("html" in alt[0] for alt in email.alternatives))

    def test_token_is_secure(self):
        """Test that generated tokens are cryptographically secure."""
        # Create multiple users and check token uniqueness and length
        tokens = set()

        for i in range(10):
            user = User.objects.create_user(
                email=f"user{i}@example.com",
                password="testpass123",
                username=f"user{i}",
            )
            user.email_verified = False
            user.email_verification_token = "initial_token"
            user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
            user.save()

            # Request verification email
            self.client.force_authenticate(user=user)
            self.client.post(self.send_verification_url)

            user.refresh_from_db()
            tokens.add(user.email_verification_token)

            # Check token is not empty and has reasonable length
            self.assertTrue(len(user.email_verification_token) >= 32)

        # All tokens should be unique
        self.assertEqual(len(tokens), 10)

    def test_user_can_login_after_verification(self):
        """Test that user can login after email verification."""
        # Create unverified user
        user = User.objects.create_user(
            email="login@example.com",
            password="testpass123",
            username="loginuser",
        )
        user.email_verified = False
        user.email_verification_token = "valid_token"
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save()

        # Verify email
        verify_url = f"/auth/verify-email/{user.email_verification_token}/"
        self.client.get(verify_url)

        # Try to login
        login_data = {"email": "login@example.com", "password": "testpass123"}
        response = self.client.post(self.login_url, login_data)

        # Should be able to login regardless of verification status
        # (you can add additional logic to prevent unverified logins if needed)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    @patch("users.views.send_mail")
    def test_email_sending_failure_handling(self, mock_send_mail):
        """Test that registration continues even if email sending fails."""
        mock_send_mail.side_effect = Exception("SMTP error")

        data = {
            "email": "failtest@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        # Registration should still succeed
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # User should be created
        user = User.objects.get(email="failtest@example.com")
        self.assertIsNotNone(user)
        self.assertFalse(user.email_verified)
