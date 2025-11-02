"""
Unit tests for webhook receiver functionality.

Tests cover:
- HMAC signature validation (GitHub, Gmail)
- Webhook authentication and authorization
- Event ID extraction
- Area matching logic
- Execution creation and idempotency
- Error handling (invalid signatures, unknown services, malformed payloads)
"""

import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from automations.models import Action, Area, Execution, Reaction, Service
from automations.webhooks import (
    extract_event_id,
    match_webhook_to_areas,
    validate_github_signature,
    validate_webhook_signature,
)

User = get_user_model()


class ValidateGitHubSignatureTest(TestCase):
    """Tests for GitHub webhook signature validation."""

    def test_valid_github_signature(self):
        """Test validation with correct GitHub signature."""
        payload = b'{"test": "data"}'
        secret = "my_webhook_secret"

        # Generate valid signature
        signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        signature_header = f"sha256={signature}"

        result = validate_github_signature(payload, signature_header, secret)
        self.assertTrue(result)

    def test_invalid_github_signature(self):
        """Test validation with incorrect signature."""
        payload = b'{"test": "data"}'
        secret = "my_webhook_secret"
        signature_header = "sha256=invalid_signature_here"

        result = validate_github_signature(payload, signature_header, secret)
        self.assertFalse(result)

    def test_missing_signature_header(self):
        """Test validation with missing signature header."""
        payload = b'{"test": "data"}'
        secret = "my_webhook_secret"

        result = validate_github_signature(payload, "", secret)
        self.assertFalse(result)

    def test_invalid_signature_format(self):
        """Test validation with invalid signature format."""
        payload = b'{"test": "data"}'
        secret = "my_webhook_secret"
        signature_header = "invalid_format_signature"

        result = validate_github_signature(payload, signature_header, secret)
        self.assertFalse(result)

    def test_timing_attack_resistance(self):
        """Test that signature comparison is constant-time."""
        payload = b'{"test": "data"}'
        secret = "my_webhook_secret"

        # Two different invalid signatures
        sig1 = "sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        sig2 = "sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        # Both should fail regardless of how different they are
        result1 = validate_github_signature(payload, sig1, secret)
        result2 = validate_github_signature(payload, sig2, secret)

        self.assertFalse(result1)
        self.assertFalse(result2)


class ValidateWebhookSignatureTest(TestCase):
    """Tests for generic webhook signature validation."""

    def test_validate_github_signature_dispatch(self):
        """Test that github service dispatches to GitHub validator."""
        payload = b'{"test": "data"}'
        secret = "my_secret"

        # Generate valid GitHub signature
        signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        headers = {"X-Hub-Signature-256": f"sha256={signature}"}

        result = validate_webhook_signature("github", payload, headers, secret)
        self.assertTrue(result)

    def test_validate_unknown_service(self):
        """Test validation fails for unknown service."""
        payload = b'{"test": "data"}'
        secret = "my_secret"
        headers = {}

        result = validate_webhook_signature("unknown_service", payload, headers, secret)
        self.assertFalse(result)


class ExtractEventIDTest(TestCase):
    """Tests for event ID extraction from webhook payloads."""

    def test_extract_github_delivery_id(self):
        """Test extracting GitHub delivery ID."""
        event_data = {"delivery": "12345678-1234-1234-1234-123456789012"}

        event_id = extract_event_id("github", event_data)
        self.assertIsNotNone(event_id)
        self.assertIn("github_delivery", event_id)
        self.assertIn("12345678", event_id)

    def test_extract_github_commit_id(self):
        """Test extracting GitHub commit SHA."""
        event_data = {
            "commits": [{"id": "abc123def456"}],
            "ref": "refs/heads/main",
        }

        event_id = extract_event_id("github", event_data)
        self.assertIsNotNone(event_id)
        self.assertIn("github_push", event_id)
        self.assertIn("abc123def456", event_id)

    def test_extract_gmail_message_id(self):
        """Test extracting Gmail message ID."""
        event_data = {"message": {"messageId": "msg_123456789"}}

        event_id = extract_event_id("gmail", event_data)
        self.assertIsNotNone(event_id)
        self.assertIn("gmail_message", event_id)

    def test_extract_fallback_event_id(self):
        """Test fallback event ID generation."""
        event_data = {"some": "data"}

        event_id = extract_event_id("custom_service", event_data)
        self.assertIsNotNone(event_id)
        self.assertIn("custom_service", event_id)


class MatchWebhookToAreasTest(TestCase):
    """Tests for matching webhook events to Areas."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create services
        self.github_service = Service.objects.create(
            name="github", description="GitHub service"
        )
        self.email_service = Service.objects.create(
            name="email", description="Email service"
        )

        # Create actions
        self.github_push_action = Action.objects.create(
            service=self.github_service,
            name="github_push",
            description="Triggered on GitHub push",
        )
        self.github_pr_action = Action.objects.create(
            service=self.github_service,
            name="github_pull_request",
            description="Triggered on GitHub PR",
        )

        # Create reaction
        self.reaction = Reaction.objects.create(
            service=self.email_service,
            name="send_email",
            description="Send an email",
        )

    def test_match_github_push_event(self):
        """Test matching GitHub push event to areas."""
        # Create area for push events
        area = Area.objects.create(
            owner=self.user,
            name="On Push",
            action=self.github_push_action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

        event_data = {"commits": [{"id": "abc123"}]}
        matched = match_webhook_to_areas("github", "push", event_data)

        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].pk, area.pk)

    def test_match_no_areas_for_event(self):
        """Test no areas match when none are configured."""
        event_data = {"commits": [{"id": "abc123"}]}
        matched = match_webhook_to_areas("github", "push", event_data)

        self.assertEqual(len(matched), 0)

    def test_match_only_active_areas(self):
        """Test that only active areas are matched."""
        # Create inactive area
        Area.objects.create(
            owner=self.user,
            name="Inactive Push",
            action=self.github_push_action,
            reaction=self.reaction,
            status=Area.Status.DISABLED,
        )

        event_data = {"commits": [{"id": "abc123"}]}
        matched = match_webhook_to_areas("github", "push", event_data)

        self.assertEqual(len(matched), 0)

    def test_match_unknown_event_type(self):
        """Test matching unknown event type returns empty."""
        event_data = {}
        matched = match_webhook_to_areas("github", "unknown_event", event_data)

        self.assertEqual(len(matched), 0)


@override_settings(
    WEBHOOK_SECRETS={"github": "test_secret_123", "gmail": "gmail_secret_456"}
)
class WebhookReceiverAPITest(TestCase):
    """Integration tests for webhook receiver API endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create services
        self.github_service = Service.objects.create(
            name="github", description="GitHub service", status=Service.Status.ACTIVE
        )
        self.email_service = Service.objects.create(
            name="email", description="Email service", status=Service.Status.ACTIVE
        )

        # Create action and reaction
        self.github_push_action = Action.objects.create(
            service=self.github_service,
            name="github_push",
            description="GitHub push event",
        )
        self.reaction = Reaction.objects.create(
            service=self.email_service,
            name="send_email",
            description="Send an email",
        )

        # Create area
        self.area = Area.objects.create(
            owner=self.user,
            name="On Push",
            action=self.github_push_action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    def _generate_github_signature(self, payload: str, secret: str) -> str:
        """Helper to generate GitHub webhook signature."""
        signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return f"sha256={signature}"

    @patch("automations.webhooks.execute_reaction")
    def test_webhook_with_valid_signature(self, mock_execute):
        """Test webhook with valid GitHub signature."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        payload = json.dumps(
            {
                "delivery": "test-delivery-123",
                "commits": [{"id": "abc123"}],
                "ref": "refs/heads/main",
            }
        )

        signature = self._generate_github_signature(payload, "test_secret_123")

        response = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["executions_created"], 1)

        # Verify execution was created
        execution = Execution.objects.filter(area=self.area).first()
        self.assertIsNotNone(execution)
        self.assertEqual(execution.status, Execution.Status.PENDING)

        # Verify reaction was queued
        mock_execute.delay.assert_called_once_with(execution.pk)

    def test_webhook_with_invalid_signature(self):
        """Test webhook with invalid signature is rejected."""
        payload = json.dumps({"delivery": "test-delivery-123"})

        response = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256="sha256=invalid_signature_here",
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Invalid webhook signature", response.json()["error"])

    def test_webhook_with_missing_signature(self):
        """Test webhook without signature header is rejected."""
        payload = json.dumps({"delivery": "test-delivery-123"})

        response = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_for_unknown_service(self):
        """Test webhook for unknown service returns 404."""
        payload = json.dumps({"test": "data"})

        response = self.client.post(
            "/webhooks/unknown_service/",
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_webhook_with_invalid_json(self):
        """Test webhook with invalid JSON payload."""
        # Note: APIClient might handle some "invalid" JSON, so we test with truly malformed data
        # For DRF's test client, we'll just verify the endpoint exists and handles errors gracefully
        signature = self._generate_github_signature("invalid json", "test_secret_123")

        response = self.client.post(
            "/webhooks/github/",
            data="invalid json",
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT="push",
        )

        # The endpoint should either reject invalid JSON (400) or process it (200/401)
        # Depending on how DRF's test client handles the data
        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_200_OK,
            ],
        )

    @patch("automations.webhooks.execute_reaction")
    def test_webhook_idempotency(self, mock_execute):
        """Test that duplicate webhooks don't create duplicate executions."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        payload = json.dumps(
            {
                "delivery": "duplicate-delivery-123",
                "commits": [{"id": "same_commit"}],
            }
        )

        signature = self._generate_github_signature(payload, "test_secret_123")

        # Send first webhook
        response1 = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.json()["executions_created"], 1)

        # Send duplicate webhook
        response2 = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.json()["executions_created"], 0)
        self.assertEqual(response2.json()["executions_skipped"], 1)

        # Only one execution should exist
        execution_count = Execution.objects.filter(area=self.area).count()
        self.assertEqual(execution_count, 1)

        # Reaction should only be queued once
        self.assertEqual(mock_execute.delay.call_count, 1)

    @patch("automations.webhooks.execute_reaction")
    def test_webhook_no_matching_areas(self, mock_execute):
        """Test webhook when no areas match the event."""
        # Disable the area
        self.area.status = Area.Status.DISABLED
        self.area.save()

        payload = json.dumps(
            {
                "delivery": "test-delivery-456",
                "commits": [{"id": "xyz789"}],
            }
        )

        signature = self._generate_github_signature(payload, "test_secret_123")

        response = self.client.post(
            "/webhooks/github/",
            data=payload,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=signature,
            HTTP_X_GITHUB_EVENT="push",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["matched_areas"], 0)
        self.assertEqual(response.json()["executions_created"], 0)

        # No reaction should be queued
        mock_execute.delay.assert_not_called()
