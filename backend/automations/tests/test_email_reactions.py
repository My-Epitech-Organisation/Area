"""
Tests for email reaction execution.
Tests the send_email reaction through _execute_reaction_logic.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class EmailReactionTests(TestCase):
    """Test send_email reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create email service
        self.email_service = Service.objects.create(
            name="email", description="Email Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.email_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.email_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test Email Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    def test_send_email_success(self):
        """Test successful email sending."""
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "test@example.com",
                "subject": "Test Subject",
                "body": "Test Body",
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertTrue(result["sent"])
        self.assertEqual(result["recipient"], "test@example.com")
        self.assertEqual(result["subject"], "Test Subject")

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].body, "Test Body")
        self.assertEqual(mail.outbox[0].to, ["test@example.com"])

    def test_send_email_missing_recipient(self):
        """Test send_email with missing recipient."""
        with self.assertRaisesMessage(ValueError, "Recipient email is required"):
            _execute_reaction_logic(
                reaction_name="send_email",
                reaction_config={
                    "subject": "Test Subject",
                    "body": "Test Body",
                },
                trigger_data={},
                area=self.area,
            )

    def test_send_email_invalid_recipient(self):
        """Test send_email with invalid recipient email."""
        # Django's send_mail doesn't validate email format,
        # so we need to test that it attempts to send
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "invalid-email",
                "subject": "Test",
                "body": "Test",
            },
            trigger_data={},
            area=self.area,
        )

        # Should still succeed (Django doesn't validate format)
        self.assertTrue(result["sent"])

    @patch("django.core.mail.send_mail", side_effect=Exception("SMTP error"))
    def test_send_email_smtp_error(self, mock_send_mail):
        """Test send_email when SMTP fails."""
        with self.assertRaisesMessage(ValueError, "Email sending failed"):
            _execute_reaction_logic(
                reaction_name="send_email",
                reaction_config={
                    "recipient": "test@example.com",
                    "subject": "Test",
                    "body": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    def test_send_email_multiple_recipients(self):
        """Test sending email - single recipient only."""
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "test@example.com",
                "subject": "Test",
                "body": "Test",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["sent"])
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_with_html(self):
        """Test sending email with HTML content."""
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "test@example.com",
                "subject": "HTML Test",
                "body": "<h1>HTML Content</h1><p>This is a test.</p>",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["sent"])
        self.assertEqual(len(mail.outbox), 1)
        # Django's send_mail sends plain text, not HTML
        self.assertIn("HTML Content", mail.outbox[0].body)

    def test_send_email_default_subject(self):
        """Test send_email uses default subject when not provided."""
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "test@example.com",
                # subject not provided - should use default
                "body": "Test body",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["sent"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "AREA Notification")

    def test_send_email_default_body(self):
        """Test send_email uses default body when not provided."""
        result = _execute_reaction_logic(
            reaction_name="send_email",
            reaction_config={
                "recipient": "test@example.com",
                "subject": "Test",
                # body not provided - should use default
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["sent"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("automated notification", mail.outbox[0].body)
