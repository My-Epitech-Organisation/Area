"""
Tests for Slack reaction execution.
Tests Slack reactions through _execute_reaction_logic.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class SlackReactionTests(TestCase):
    """Test Slack reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create Slack service
        self.slack_service = Service.objects.create(
            name="slack", description="Slack Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.slack_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.slack_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test Slack Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_message_success(self, mock_post_message, mock_get_token):
        """Test successful Slack message sending."""
        mock_get_token.return_value = "test_slack_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_send_message",
            reaction_config={
                "channel": "#general",
                "message": "Test message",
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["channel"], "#general")
        self.assertEqual(result["message"], "Test message")
        self.assertEqual(result["message_ts"], "1234567890.123456")

        # Verify API was called correctly
        mock_get_token.assert_called_once_with(self.user, "slack")
        mock_post_message.assert_called_once_with(
            "test_slack_token", "#general", "Test message"
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_slack_send_message_missing_channel(self, mock_get_token):
        """Test slack_send_message with missing channel."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Channel is required for slack_send_message"
        ):
            _execute_reaction_logic(
                reaction_name="slack_send_message",
                reaction_config={
                    "message": "Test message",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_slack_send_message_no_token(self, mock_get_token):
        """Test slack_send_message when user has no Slack token."""
        mock_get_token.return_value = None

        with self.assertRaisesMessage(ValueError, "No valid Slack token"):
            _execute_reaction_logic(
                reaction_name="slack_send_message",
                reaction_config={
                    "channel": "#general",
                    "message": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_message_api_error(self, mock_post_message, mock_get_token):
        """Test slack_send_message when API fails."""
        mock_get_token.return_value = "test_token"
        mock_post_message.side_effect = Exception("channel_not_found")

        with self.assertRaisesMessage(ValueError, "Slack send_message failed"):
            _execute_reaction_logic(
                reaction_name="slack_send_message",
                reaction_config={
                    "channel": "#nonexistent",
                    "message": "Test",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_message_default_message(self, mock_post_message, mock_get_token):
        """Test slack_send_message uses default message when not provided."""
        mock_get_token.return_value = "test_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_send_message",
            reaction_config={
                "channel": "#general",
                # message not provided - should use default
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        # Verify default message was used
        mock_post_message.assert_called_once()
        call_args = mock_post_message.call_args[0]
        self.assertEqual(call_args[2], "AREA triggered")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_alert_success(self, mock_post_message, mock_get_token):
        """Test successful Slack alert sending."""
        mock_get_token.return_value = "test_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_send_alert",
            reaction_config={
                "channel": "#alerts",
                "alert_type": "warning",
                "title": "System Alert",
                "details": "CPU usage high",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["channel"], "#alerts")
        self.assertEqual(result["alert_type"], "warning")
        self.assertEqual(result["title"], "System Alert")

        # Verify API was called with attachments
        mock_post_message.assert_called_once()
        call_args = mock_post_message.call_args
        self.assertIn("attachments", call_args[1])

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_alert_info_type(self, mock_post_message, mock_get_token):
        """Test slack_send_alert with info alert type."""
        mock_get_token.return_value = "test_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_send_alert",
            reaction_config={
                "channel": "#general",
                "alert_type": "info",
                "title": "Info Alert",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["alert_type"], "info")

        # Verify color is "good" for info
        call_args = mock_post_message.call_args
        attachment = call_args[1]["attachments"][0]
        self.assertEqual(attachment["color"], "good")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_send_alert_error_type(self, mock_post_message, mock_get_token):
        """Test slack_send_alert with error alert type."""
        mock_get_token.return_value = "test_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_send_alert",
            reaction_config={
                "channel": "#errors",
                "alert_type": "error",
                "title": "Critical Error",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])

        # Verify color is "danger" for error
        call_args = mock_post_message.call_args
        attachment = call_args[1]["attachments"][0]
        self.assertEqual(attachment["color"], "danger")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.slack_helper.post_message")
    def test_slack_post_update_success(self, mock_post_message, mock_get_token):
        """Test successful Slack update posting."""
        mock_get_token.return_value = "test_token"
        mock_post_message.return_value = {"ts": "1234567890.123456"}

        result = _execute_reaction_logic(
            reaction_name="slack_post_update",
            reaction_config={
                "channel": "#updates",
                "title": "Deployment Update",
                "status": "Completed",
                "details": "Version 1.2.3 deployed",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["channel"], "#updates")
        self.assertEqual(result["title"], "Deployment Update")
        self.assertEqual(result["status"], "Completed")

        # Verify message formatting
        mock_post_message.assert_called_once()
        call_args = mock_post_message.call_args[0]
        message_text = call_args[2]
        self.assertIn("Deployment Update", message_text)
        self.assertIn("Completed", message_text)
