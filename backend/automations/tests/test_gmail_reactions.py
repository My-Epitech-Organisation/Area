"""
Tests for Gmail reaction execution.
Tests Gmail reactions through _execute_reaction_logic.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class GmailReactionTests(TestCase):
    """Test Gmail reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create Gmail/Google service
        self.gmail_service = Service.objects.create(
            name="gmail", description="Gmail Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.gmail_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.gmail_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test Gmail Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.send_email")
    def test_gmail_send_email_success(self, mock_send_email, mock_get_token):
        """Test successful Gmail email sending."""
        mock_get_token.return_value = "test_google_token"
        mock_send_email.return_value = {"id": "msg_123456"}

        result = _execute_reaction_logic(
            reaction_name="gmail_send_email",
            reaction_config={
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test email body",
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["to"], "recipient@example.com")
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["message_id"], "msg_123456")

        # Verify API was called correctly
        mock_get_token.assert_called_once_with(self.user, "google")
        mock_send_email.assert_called_once_with(
            "test_google_token",
            "recipient@example.com",
            "Test Subject",
            "Test email body",
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_gmail_send_email_missing_recipient(self, mock_get_token):
        """Test gmail_send_email with missing recipient."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Recipient email is required for gmail_send_email"
        ):
            _execute_reaction_logic(
                reaction_name="gmail_send_email",
                reaction_config={
                    "subject": "Test",
                    "body": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_gmail_send_email_no_token(self, mock_get_token):
        """Test gmail_send_email when user has no Google token."""
        mock_get_token.return_value = None

        with self.assertRaisesMessage(ValueError, "No valid Google token"):
            _execute_reaction_logic(
                reaction_name="gmail_send_email",
                reaction_config={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.send_email")
    def test_gmail_send_email_api_error(self, mock_send_email, mock_get_token):
        """Test gmail_send_email when API fails."""
        mock_get_token.return_value = "test_token"
        mock_send_email.side_effect = Exception("API error")

        with self.assertRaisesMessage(ValueError, "Gmail send failed"):
            _execute_reaction_logic(
                reaction_name="gmail_send_email",
                reaction_config={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.send_email")
    def test_gmail_send_email_default_subject(self, mock_send_email, mock_get_token):
        """Test gmail_send_email uses default subject when not provided."""
        mock_get_token.return_value = "test_token"
        mock_send_email.return_value = {"id": "msg_123"}

        result = _execute_reaction_logic(
            reaction_name="gmail_send_email",
            reaction_config={
                "to": "test@example.com",
                # subject not provided
                "body": "Test",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        # Verify default subject was used
        call_args = mock_send_email.call_args[0]
        self.assertEqual(call_args[2], "AREA Notification")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.mark_message_read")
    def test_gmail_mark_read_success(self, mock_mark_read, mock_get_token):
        """Test successful Gmail mark as read."""
        mock_get_token.return_value = "test_token"

        result = _execute_reaction_logic(
            reaction_name="gmail_mark_read",
            reaction_config={
                "message_id": "msg_123",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], "msg_123")

        mock_mark_read.assert_called_once_with("test_token", "msg_123")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.mark_message_read")
    def test_gmail_mark_read_from_trigger_data(self, mock_mark_read, mock_get_token):
        """Test gmail_mark_read getting message_id from trigger_data."""
        mock_get_token.return_value = "test_token"

        result = _execute_reaction_logic(
            reaction_name="gmail_mark_read",
            reaction_config={},  # No message_id in config
            trigger_data={"message_id": "msg_from_trigger"},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], "msg_from_trigger")

        mock_mark_read.assert_called_once_with("test_token", "msg_from_trigger")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_gmail_mark_read_no_message_id(self, mock_get_token):
        """Test gmail_mark_read with no message_id."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(ValueError, "Message ID required"):
            _execute_reaction_logic(
                reaction_name="gmail_mark_read",
                reaction_config={},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.add_label_to_message")
    def test_gmail_add_label_success(self, mock_add_label, mock_get_token):
        """Test successful Gmail add label."""
        mock_get_token.return_value = "test_token"

        result = _execute_reaction_logic(
            reaction_name="gmail_add_label",
            reaction_config={
                "message_id": "msg_123",
                "label": "Important",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["message_id"], "msg_123")
        self.assertEqual(result["label"], "Important")

        mock_add_label.assert_called_once_with("test_token", "msg_123", "Important")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_gmail_add_label_missing_params(self, mock_get_token):
        """Test gmail_add_label with missing parameters."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Message ID and label required for gmail_add_label"
        ):
            _execute_reaction_logic(
                reaction_name="gmail_add_label",
                reaction_config={
                    "message_id": "msg_123",
                    # label missing
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.gmail_helper.add_label_to_message")
    def test_gmail_add_label_api_error(self, mock_add_label, mock_get_token):
        """Test gmail_add_label when API fails."""
        mock_get_token.return_value = "test_token"
        mock_add_label.side_effect = Exception("Label not found")

        with self.assertRaisesMessage(ValueError, "Gmail add_label failed"):
            _execute_reaction_logic(
                reaction_name="gmail_add_label",
                reaction_config={
                    "message_id": "msg_123",
                    "label": "NonExistent",
                },
                trigger_data={},
                area=self.area,
            )
