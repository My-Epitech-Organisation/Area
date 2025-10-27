"""
Tests for email verification enforcement in API endpoints.

Tests that endpoints correctly block unverified users and allow verified users.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from automations.models import Service
from users.models import ServiceToken

User = get_user_model()


class EmailVerificationEnforcementTestCase(APITestCase):
    """Test that email verification is enforced on protected endpoints."""

    def setUp(self):
        """Create test users - one verified, one unverified."""
        self.verified_user = User.objects.create_user(
            email="verified@example.com",
            password="testpass123",
            username="verified_user",
            email_verified=True,  # Verified
        )

        self.unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password="testpass123",
            username="unverified_user",
            email_verified=False,  # NOT verified
        )

        # Create a test service
        self.service = Service.objects.create(
            name="test_service", description="Test service", status="active"
        )

    def get_token_for_user(self, user):
        """Get JWT access token for a user."""
        response = self.client.post(
            "/auth/login/",
            {"email": user.email, "password": "testpass123"},
            format="json",
        )
        return response.data["access"]

    def test_unverified_user_blocked_from_services(self):
        """Unverified user should NOT access /api/services/."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/services/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Email verification required", response.data["detail"])

    def test_verified_user_can_access_services(self):
        """Verified user SHOULD access /api/services/."""
        token = self.get_token_for_user(self.verified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/services/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unverified_user_blocked_from_actions(self):
        """Unverified user should NOT access /api/actions/."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/actions/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_blocked_from_reactions(self):
        """Unverified user should NOT access /api/reactions/."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/reactions/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_blocked_from_areas(self):
        """Unverified user should NOT access /api/areas/."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/areas/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_blocked_from_oauth_initiate(self):
        """Unverified user should NOT start OAuth flow."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/auth/oauth/google/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unverified_user_can_resend_verification(self):
        """Unverified user SHOULD be able to request verification email."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post("/auth/resend-verification/")

        # Should succeed (200 or 201)
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )

    def test_superuser_bypasses_verification(self):
        """Superuser should bypass email verification requirement."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            email_verified=False,  # NOT verified but is superuser
        )

        token = self.get_token_for_user(superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/services/")

        # Superuser should have access despite not being verified
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_bypasses_verification(self):
        """Staff user should bypass email verification requirement."""
        staff_user = User.objects.create_user(
            email="staff@example.com",
            password="staffpass123",
            email_verified=False,  # NOT verified
            is_staff=True,  # But is staff
        )

        token = self.get_token_for_user(staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/services/")

        # Staff should have access despite not being verified
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_endpoints_accessible_without_verification(self):
        """Public endpoints should be accessible without verification."""
        # About.json should be public (no auth required)
        response = self.client.get("/about.json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Health check should be public
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error_message_includes_helpful_info(self):
        """Error message should guide user to verification."""
        token = self.get_token_for_user(self.unverified_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/services/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        error_msg = response.data["detail"].lower()

        # Check that error message mentions verification
        self.assertIn("email verification", error_msg)
        self.assertIn("verify", error_msg)
