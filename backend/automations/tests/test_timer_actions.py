"""
Unit tests for timer action implementation.

Tests cover:
- Timer configuration validation
- Timer triggering logic (daily, weekly)
- Edge cases (midnight, week boundaries)
- Timezone handling
- Integration flow (trigger → execution → reaction)
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from automations.models import Action, Area, Execution, Reaction, Service
from automations.tasks import (
    handle_timer_action,
    validate_timer_config,
)

User = get_user_model()


class ValidateTimerConfigTest(TestCase):
    """Tests for validate_timer_config() function."""

    def test_validate_daily_timer_valid(self):
        """Test valid timer_daily configuration."""
        is_valid, error = validate_timer_config(
            "timer_daily", {"hour": 14, "minute": 30}
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_daily_timer_missing_hour(self):
        """Test timer_daily with missing hour."""
        is_valid, error = validate_timer_config("timer_daily", {"minute": 30})
        self.assertFalse(is_valid)
        self.assertIn("hour is required", error)

    def test_validate_daily_timer_missing_minute(self):
        """Test timer_daily with missing minute."""
        is_valid, error = validate_timer_config("timer_daily", {"hour": 14})
        self.assertFalse(is_valid)
        self.assertIn("minute is required", error)

    def test_validate_daily_timer_invalid_hour(self):
        """Test timer_daily with invalid hour."""
        is_valid, error = validate_timer_config(
            "timer_daily", {"hour": 25, "minute": 30}
        )
        self.assertFalse(is_valid)
        self.assertIn("hour must be an integer between 0 and 23", error)

    def test_validate_daily_timer_invalid_minute(self):
        """Test timer_daily with invalid minute."""
        is_valid, error = validate_timer_config(
            "timer_daily", {"hour": 14, "minute": 60}
        )
        self.assertFalse(is_valid)
        self.assertIn("minute must be an integer between 0 and 59", error)

    def test_validate_daily_timer_negative_hour(self):
        """Test timer_daily with negative hour."""
        is_valid, error = validate_timer_config(
            "timer_daily", {"hour": -1, "minute": 30}
        )
        self.assertFalse(is_valid)
        self.assertIn("hour must be an integer between 0 and 23", error)

    def test_validate_weekly_timer_valid(self):
        """Test valid timer_weekly configuration."""
        is_valid, error = validate_timer_config(
            "timer_weekly", {"hour": 9, "minute": 0, "day_of_week": 0}
        )
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_weekly_timer_missing_day_of_week(self):
        """Test timer_weekly with missing day_of_week."""
        is_valid, error = validate_timer_config(
            "timer_weekly", {"hour": 9, "minute": 0}
        )
        self.assertFalse(is_valid)
        self.assertIn("day_of_week is required", error)

    def test_validate_weekly_timer_invalid_day_of_week(self):
        """Test timer_weekly with invalid day_of_week."""
        is_valid, error = validate_timer_config(
            "timer_weekly", {"hour": 9, "minute": 0, "day_of_week": 7}
        )
        self.assertFalse(is_valid)
        self.assertIn("day_of_week must be an integer between 0 and 6", error)

    def test_validate_timer_empty_config(self):
        """Test with empty action_config."""
        is_valid, error = validate_timer_config("timer_daily", {})
        self.assertFalse(is_valid)
        self.assertIn("action_config is required", error)

    def test_validate_timer_none_config(self):
        """Test with None action_config."""
        is_valid, error = validate_timer_config("timer_daily", None)
        self.assertFalse(is_valid)
        self.assertIn("action_config is required", error)


class HandleTimerActionTest(TestCase):
    """Tests for handle_timer_action() function."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create services
        self.timer_service = Service.objects.create(
            name="timer", description="Timer service"
        )
        self.webhook_service = Service.objects.create(
            name="webhook", description="Webhook service"
        )

        # Create actions and reactions
        self.action_daily = Action.objects.create(
            service=self.timer_service,
            name="timer_daily",
            description="Trigger at specific time daily",
        )
        self.action_weekly = Action.objects.create(
            service=self.timer_service,
            name="timer_weekly",
            description="Trigger at specific time weekly",
        )
        self.reaction = Reaction.objects.create(
            service=self.webhook_service,
            name="webhook_post",
            description="Send HTTP POST webhook",
        )

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_handle_daily_timer_triggers_at_correct_time(self, mock_execute):
        """Test daily timer triggers at configured time."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        area = Area.objects.create(
            owner=self.user,
            name="Daily 14:30",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.area, area)
        self.assertEqual(execution.status, Execution.Status.PENDING)
        self.assertIn("timestamp", execution.trigger_data)
        self.assertIn("triggered_at", execution.trigger_data)

        # Verify execute_reaction was called
        mock_execute.delay.assert_called_once_with(execution.pk)

    @freeze_time("2024-01-15 14:31:00")
    @patch("automations.tasks.execute_reaction")
    def test_handle_daily_timer_does_not_trigger_at_wrong_time(self, mock_execute):
        """Test daily timer does not trigger at wrong time."""
        area = Area.objects.create(
            owner=self.user,
            name="Daily 14:30",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNone(execution)
        mock_execute.delay.assert_not_called()

    @freeze_time("2024-01-15 00:00:00")  # Monday at midnight
    @patch("automations.tasks.execute_reaction")
    def test_handle_weekly_timer_triggers_on_correct_day(self, mock_execute):
        """Test weekly timer triggers on correct day and time."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        area = Area.objects.create(
            owner=self.user,
            name="Weekly Monday 00:00",
            action=self.action_weekly,
            reaction=self.reaction,
            action_config={"hour": 0, "minute": 0, "day_of_week": 0},  # Monday
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.area, area)
        mock_execute.delay.assert_called_once_with(execution.pk)

    @freeze_time("2024-01-16 00:00:00")  # Tuesday at midnight
    @patch("automations.tasks.execute_reaction")
    def test_handle_weekly_timer_does_not_trigger_on_wrong_day(self, mock_execute):
        """Test weekly timer does not trigger on wrong day."""
        area = Area.objects.create(
            owner=self.user,
            name="Weekly Monday 00:00",
            action=self.action_weekly,
            reaction=self.reaction,
            action_config={"hour": 0, "minute": 0, "day_of_week": 0},  # Monday
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()  # Tuesday
        execution = handle_timer_action(area, current_time)

        self.assertIsNone(execution)
        mock_execute.delay.assert_not_called()

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_handle_timer_with_invalid_config_returns_none(self, mock_execute):
        """Test timer with invalid config returns None."""
        area = Area.objects.create(
            owner=self.user,
            name="Invalid Timer",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 25, "minute": 30},  # Invalid hour
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNone(execution)
        mock_execute.delay.assert_not_called()

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_handle_timer_idempotency(self, mock_execute):
        """Test that calling handle_timer_action twice doesn't create duplicates."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        area = Area.objects.create(
            owner=self.user,
            name="Daily 14:30",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()

        # First call - should create execution
        execution1 = handle_timer_action(area, current_time)
        self.assertIsNotNone(execution1)

        # Second call - should return None (idempotency)
        execution2 = handle_timer_action(area, current_time)
        self.assertIsNone(execution2)

        # Only one execution should exist
        self.assertEqual(Execution.objects.filter(area=area).count(), 1)

        # execute_reaction should be called only once
        self.assertEqual(mock_execute.delay.call_count, 1)

    @freeze_time("2024-01-15 23:59:00")
    @patch("automations.tasks.execute_reaction")
    def test_handle_timer_at_day_boundary(self, mock_execute):
        """Test timer at day boundary (23:59)."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        area = Area.objects.create(
            owner=self.user,
            name="Daily 23:59",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 23, "minute": 59},
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.trigger_data["triggered_at"]["hour"], 23)
        self.assertEqual(execution.trigger_data["triggered_at"]["minute"], 59)

    @freeze_time("2024-01-21 23:59:00")  # Sunday at 23:59
    @patch("automations.tasks.execute_reaction")
    def test_handle_weekly_timer_at_week_boundary(self, mock_execute):
        """Test weekly timer at week boundary (Sunday 23:59)."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        area = Area.objects.create(
            owner=self.user,
            name="Weekly Sunday 23:59",
            action=self.action_weekly,
            reaction=self.reaction,
            action_config={"hour": 23, "minute": 59, "day_of_week": 6},  # Sunday
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        self.assertIsNotNone(execution)
        self.assertEqual(execution.trigger_data["triggered_at"]["weekday"], 6)


class TimerActionIntegrationTest(TestCase):
    """Integration tests for timer action flow."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create services
        self.timer_service = Service.objects.create(
            name="timer", description="Timer service"
        )
        self.webhook_service = Service.objects.create(
            name="webhook", description="Webhook service"
        )

        # Create actions and reactions
        self.action_daily = Action.objects.create(
            service=self.timer_service,
            name="timer_daily",
            description="Trigger at specific time daily",
        )
        self.reaction = Reaction.objects.create(
            service=self.webhook_service,
            name="webhook_post",
            description="Send HTTP POST webhook",
        )

    @freeze_time("2024-01-15 09:00:00")
    @patch("automations.tasks.execute_reaction")
    def test_full_timer_execution_flow(self, mock_execute):
        """Test complete flow: timer trigger → execution created → reaction queued."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        # Create area
        area = Area.objects.create(
            owner=self.user,
            name="Morning Alert",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 9, "minute": 0},
            reaction_config={"url": "https://example.com/webhook"},
            status=Area.Status.ACTIVE,
        )

        # Trigger timer
        current_time = timezone.now()
        execution = handle_timer_action(area, current_time)

        # Verify execution was created
        self.assertIsNotNone(execution)
        self.assertEqual(execution.area, area)
        self.assertEqual(execution.status, Execution.Status.PENDING)

        # Verify trigger data
        self.assertEqual(execution.trigger_data["action_type"], "timer_daily")
        self.assertEqual(execution.trigger_data["action_config"]["hour"], 9)
        self.assertEqual(execution.trigger_data["action_config"]["minute"], 0)

        # Verify external_event_id format
        expected_event_id = f"timer_{area.pk}_202401150900"
        self.assertEqual(execution.external_event_id, expected_event_id)

        # Verify reaction was queued
        mock_execute.delay.assert_called_once_with(execution.pk)

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_multiple_areas_same_time(self, mock_execute):
        """Test multiple areas triggering at the same time."""
        mock_execute.delay.return_value = MagicMock(id="task-123")

        # Create multiple areas with same schedule
        area1 = Area.objects.create(
            owner=self.user,
            name="Alert 1",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        area2 = Area.objects.create(
            owner=self.user,
            name="Alert 2",
            action=self.action_daily,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        current_time = timezone.now()

        # Trigger both timers
        execution1 = handle_timer_action(area1, current_time)
        execution2 = handle_timer_action(area2, current_time)

        # Both should create executions
        self.assertIsNotNone(execution1)
        self.assertIsNotNone(execution2)

        # Executions should be different
        self.assertNotEqual(execution1.pk, execution2.pk)

        # Both reactions should be queued
        self.assertEqual(mock_execute.delay.call_count, 2)
