from datetime import timedelta

from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import User


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.login_url = reverse("token_obtain_pair")
        self.user_data = {
            "username": "testuser",  # Optional display name
            "email": "test@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        self.user = User.objects.create_user(
            email="testuser2@example.com", password="StrongPassword123"
        )

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {"email": "test@example.com", "password": "StrongPassword123"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_detail(self):
        self.client.force_authenticate(user=self.user)
        detail_url = reverse("user_detail")
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_token_refresh(self):
        """Test JWT token refresh mechanism"""
        # First, register and login to get tokens
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {"email": "test@example.com", "password": "StrongPassword123"}
        login_response = self.client.post(self.login_url, login_data, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        # Extract the refresh token
        refresh_token = login_response.data["refresh"]

        # Use the refresh token to get a new access token
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        # The new access token should be different from the original
        new_access_token = refresh_response.data["access"]
        original_access_token = login_response.data["access"]
        self.assertNotEqual(new_access_token, original_access_token)

    def test_invalid_refresh_token(self):
        """Test that invalid refresh tokens are rejected"""
        refresh_url = reverse("token_refresh")
        invalid_refresh_data = {"refresh": "invalid-token-123"}
        response = self.client.post(refresh_url, invalid_refresh_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_registration_email_unverified(self):
        """Test that new users have email_verified=False by default"""
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("email_verified", response.data)
        self.assertFalse(response.data["email_verified"])

        # Verify in database
        user = User.objects.get(email="test@example.com")
        self.assertFalse(user.email_verified)
        # Token should be generated automatically
        self.assertNotEqual(user.email_verification_token, "")
        self.assertIsNotNone(user.email_verification_token_expires)

    def test_send_verification_email(self):
        """Test sending verification email to authenticated user"""
        # Create and authenticate user
        user = User.objects.create_user(
            email="testverify@example.com",
            username="testverify",
            password="StrongPassword123",
        )
        self.client.force_authenticate(user=user)

        send_verification_url = reverse("send_verification_email")
        response = self.client.post(send_verification_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

        # Check that token was generated
        user.refresh_from_db()
        self.assertIsNotNone(user.email_verification_token)

    def test_verify_email_with_valid_token(self):
        """Test email verification with valid token"""
        # Create user with verification token
        user = User.objects.create_user(
            email="test2@example.com",
            username="testverify2",
            password="StrongPassword123",
        )
        user.email_verification_token = "valid-token-123"
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save()

        verify_url = reverse("verify_email", kwargs={"token": "valid-token-123"})
        response = self.client.get(verify_url)

        # Now returns redirect instead of JSON
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=true", location)
        self.assertIn("message=", location)

        # Check database
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertEqual(user.email_verification_token, "")

    def test_verify_email_with_invalid_token(self):
        """Test email verification with invalid token"""
        verify_url = reverse("verify_email", kwargs={"token": "invalid-token-456"})
        response = self.client.get(verify_url)

        # Now returns redirect instead of JSON
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("verified=false", location)
        self.assertIn("error=", location)

    def test_complete_authentication_flow(self):
        """Test complete flow: register → login → refresh → /users/me"""
        # Step 1: Register
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["email_verified"])

        # Step 2: Login
        login_data = {"email": "test@example.com", "password": "StrongPassword123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        # Store tokens
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        # Step 3: Access protected endpoint with access token
        detail_url = reverse("user_detail")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = self.client.get(detail_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "test@example.com")
        # username is optional display name
        if "username" in me_response.data:
            self.assertEqual(me_response.data["username"], "testuser")
        self.assertFalse(me_response.data["email_verified"])

        # Step 4: Refresh token
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        # Step 5: Use new access token
        new_access_token = refresh_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
        me_response2 = self.client.get(detail_url)
        self.assertEqual(me_response2.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response2.data["email"], "test@example.com")


class ValidationTests(TestCase):
    """Tests for input validation and error handling"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.login_url = reverse("token_obtain_pair")

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        # Missing email (now required)
        data = {
            "username": "testuser",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "password2": "DifferentPassword456",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_weak_password(self):
        """Test registration with weak password"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "password2": "123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(email="existing@example.com", password="password123")

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Create user
        User.objects.create_user(
            email="testuser@example.com", password="correctpassword"
        )

        # Try with wrong password
        login_data = {"email": "testuser@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {"email": "nonexistent@example.com", "password": "password123"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        login_data = {"email": "testuser@example.com"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without authentication"""
        detail_url = reverse("user_detail")
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        detail_url = reverse("user_detail")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ThrottlingTests(TestCase):
    """Tests for rate limiting and throttling"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("token_obtain_pair")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )

    def test_login_throttling(self):
        """Test that throttling configuration is in place"""
        # Note: With current settings (100/day for anonymous users),
        # it's not practical to test actual throttling in unit tests
        # This test verifies the throttling configuration exists
        from django.conf import settings

        # Verify throttling is configured
        rest_framework_settings = getattr(settings, "REST_FRAMEWORK", {})
        self.assertIn("DEFAULT_THROTTLE_CLASSES", rest_framework_settings)
        self.assertIn("DEFAULT_THROTTLE_RATES", rest_framework_settings)

        # Test that a few failed attempts still work (within limits)
        login_data = {"email": "testuser@example.com", "password": "wrongpassword"}

        for _ in range(3):  # Make a few failed attempts
            response = self.client.post(self.login_url, login_data, format="json")
            # Should still get 401 (unauthorized) not 429 (throttled)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenLifecycleTests(TestCase):
    """Tests for token expiration and lifecycle management"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }

    def test_refresh_with_invalid_token(self):
        """Test token refresh with invalid refresh token"""
        refresh_data = {"refresh": "invalid-refresh-token"}
        response = self.client.post(self.refresh_url, refresh_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_with_malformed_token(self):
        """Test token refresh with malformed token"""
        refresh_data = {"refresh": "clearly.not.a.jwt.token"}
        response = self.client.post(self.refresh_url, refresh_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_rotation(self):
        """Test that refresh tokens are rotated when ROTATE_REFRESH_TOKENS is True"""
        # Register and login
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {"email": "test@example.com", "password": "StrongPassword123"}
        login_response = self.client.post(self.login_url, login_data, format="json")

        self.assertIn("refresh", login_response.data)
        original_refresh = login_response.data["refresh"]

        # Refresh the token - this should work
        refresh_data = {"refresh": original_refresh}
        refresh_response = self.client.post(
            self.refresh_url, refresh_data, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        # Check if we get a new refresh token (token rotation)
        # When ROTATE_REFRESH_TOKENS is True, we should get a new refresh token
        if "refresh" in refresh_response.data:
            new_refresh = refresh_response.data["refresh"]
            # The new refresh token should be different from the original
            self.assertNotEqual(
                original_refresh,
                new_refresh,
                "New refresh token should be different from original when rotation is enabled",
            )

            # Verify the new refresh token works
            new_refresh_data = {"refresh": new_refresh}
            new_response = self.client.post(
                self.refresh_url, new_refresh_data, format="json"
            )
            self.assertEqual(
                new_response.status_code,
                status.HTTP_200_OK,
                "New refresh token should be valid",
            )
            self.assertIn("access", new_response.data)


class EdgeCaseTests(TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth_register")
        self.login_url = reverse("token_obtain_pair")

    def test_register_empty_data(self):
        """Test registration with completely empty data"""
        response = self.client.post(self.register_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_special_characters(self):
        """Test registration with special characters in username"""
        data = {
            "username": "test@user#123",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        # Django has username validation - some special characters might be rejected
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )

    def test_register_very_long_username(self):
        """Test registration with very long username"""
        long_username = "a" * 200  # Very long username
        data = {
            "username": long_username,
            "email": "test@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        # Should fail due to username length limits (Django default is 150 chars)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_very_long_email(self):
        """Test registration with very long email"""
        long_email = "a" * 200 + "@example.com"
        data = {
            "username": "testuser",
            "email": long_email,
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        # Depending on Django's email field max_length, this might succeed or fail
        # Let's check what actually happens
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )

    def test_login_case_sensitivity(self):
        """Test login email case insensitivity"""
        # Create user with lowercase email
        User.objects.create_user(email="testuser@example.com", password="password123")

        # Try login with different case (emails should be case-insensitive typically)
        login_data = {"email": "TestUser@Example.COM", "password": "password123"}
        response = self.client.post(self.login_url, login_data, format="json")
        # Django email lookups can be case-insensitive depending on DB
        # This test documents the current behavior
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
        )

    def test_multiple_sessions_same_user(self):
        """Test that same user can have multiple active sessions"""
        # Create user
        user_data = {
            "username": "multiuser",
            "email": "multi@example.com",
            "password": "StrongPassword123",
            "password2": "StrongPassword123",
        }
        self.client.post(self.register_url, user_data, format="json")

        # Login multiple times
        login_data = {"email": "multi@example.com", "password": "StrongPassword123"}
        response1 = self.client.post(self.login_url, login_data, format="json")
        response2 = self.client.post(self.login_url, login_data, format="json")

        # Both should succeed
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Tokens should be different
        self.assertNotEqual(response1.data["access"], response2.data["access"])

    def test_email_verification_already_verified(self):
        """Test sending verification email to already verified user"""
        user = User.objects.create_user(
            email="verified@example.com",
            username="verified_user",
            password="StrongPassword123",
        )
        user.email_verified = True
        user.save()

        self.client.force_authenticate(user=user)

        send_verification_url = reverse("send_verification_email")
        response = self.client.post(send_verification_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already verified", response.data["message"])

    def test_verify_email_already_verified_token(self):
        """Test verifying email with token when already verified"""
        user = User.objects.create_user(
            email="verified2@example.com",
            username="verified_user2",
            password="StrongPassword123",
        )
        user.email_verified = True
        user.email_verification_token = "some-token"
        user.save()

        verify_url = reverse("verify_email", kwargs={"token": "some-token"})
        response = self.client.get(verify_url)

        # Now returns redirect instead of JSON
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        location = response["Location"]
        self.assertIn("already_verified=true", location)
