"""
Unit tests for Celery tasks.

Tests cover:
- Helper functions (create_execution_safe, get_active_areas, should_trigger_timer)
- Timer action checking and triggering
- Idempotency of execution creation
- Reaction execution flow
- Error handling and retries
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from django.test import TestCase, override_settings
from django.utils import timezone

from automations.models import Action, Area, Execution, Reaction, Service
from automations.tasks import (
    check_timer_actions,
    create_execution_safe,
    execute_reaction,
    get_active_areas,
    should_trigger_timer,
    test_execution_flow,
)
from users.models import User


# Override Celery to run tasks synchronously in tests
@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class TaskHelperFunctionsTest(TestCase):
    """Test helper functions used by tasks."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )

        self.service = Service.objects.create(
            name="TestService",
            description="Test service",
            status=Service.Status.ACTIVE,
        )

        self.action = Action.objects.create(
            service=self.service, name="timer_daily", description="Daily timer"
        )

        self.reaction = Reaction.objects.create(
            service=self.service, name="log_message", description="Log a message"
        )

        self.area = Area.objects.create(
            owner=self.user,
            name="Test Area",
            action=self.action,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            reaction_config={"message": "Test message"},
            status=Area.Status.ACTIVE,
        )

    def test_create_execution_safe_success(self):
        """Test creating a new execution successfully."""
        execution, created = create_execution_safe(
            area=self.area,
            external_event_id="test_event_001",
            trigger_data={"test": "data"},
        )

        self.assertIsNotNone(execution)
        self.assertTrue(created)
        self.assertEqual(execution.area, self.area)
        self.assertEqual(execution.external_event_id, "test_event_001")
        self.assertEqual(execution.status, Execution.Status.PENDING)

    def test_create_execution_safe_duplicate(self):
        """Test idempotency - duplicate event_id returns existing execution."""
        # Create first execution
        exec1, created1 = create_execution_safe(
            area=self.area,
            external_event_id="duplicate_event",
            trigger_data={"test": "data1"},
        )

        self.assertTrue(created1)

        # Try to create duplicate
        exec2, created2 = create_execution_safe(
            area=self.area,
            external_event_id="duplicate_event",
            trigger_data={"test": "data2"},
        )

        self.assertIsNone(exec2)
        self.assertFalse(created2)

        # Verify only one execution exists
        self.assertEqual(Execution.objects.count(), 1)

    def test_get_active_areas(self):
        """Test getting active areas by action name."""
        # Create additional areas
        action2 = Action.objects.create(
            service=self.service, name="timer_weekly", description="Weekly timer"
        )

        area2 = Area.objects.create(
            owner=self.user,
            name="Weekly Area",
            action=action2,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

        # Disabled area should not be returned
        area3 = Area.objects.create(
            owner=self.user,
            name="Disabled Area",
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.DISABLED,
        )

        # Get active timer areas
        areas = get_active_areas(["timer_daily", "timer_weekly"])

        self.assertEqual(len(areas), 2)
        area_ids = [a.pk for a in areas]
        self.assertIn(self.area.pk, area_ids)
        self.assertIn(area2.pk, area_ids)
        self.assertNotIn(area3.pk, area_ids)

    def test_should_trigger_timer_daily_match(self):
        """Test timer_daily triggers at correct time."""
        # Configure for 14:30
        self.area.action_config = {"hour": 14, "minute": 30}
        self.area.save()

        # Test at exact time
        test_time = timezone.now().replace(hour=14, minute=30, second=0, microsecond=0)
        self.assertTrue(should_trigger_timer(self.area, test_time))

    def test_should_trigger_timer_daily_no_match(self):
        """Test timer_daily does not trigger at wrong time."""
        self.area.action_config = {"hour": 14, "minute": 30}
        self.area.save()

        # Test at different time
        test_time = timezone.now().replace(hour=15, minute=30)
        self.assertFalse(should_trigger_timer(self.area, test_time))

    def test_should_trigger_timer_weekly_match(self):
        """Test timer_weekly triggers on correct day and time."""
        # Monday at 10:00
        self.area.action.name = "timer_weekly"
        self.area.action.save()
        self.area.action_config = {"day_of_week": 0, "hour": 10, "minute": 0}
        self.area.save()

        # Create a Monday at 10:00
        test_time = timezone.now()
        # Find next Monday
        days_ahead = 0 - test_time.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        test_time = test_time + timedelta(days=days_ahead)
        test_time = test_time.replace(hour=10, minute=0, second=0, microsecond=0)

        self.assertTrue(should_trigger_timer(self.area, test_time))

    def test_should_trigger_timer_weekly_wrong_day(self):
        """Test timer_weekly does not trigger on wrong day."""
        self.area.action.name = "timer_weekly"
        self.area.action.save()
        self.area.action_config = {"day_of_week": 0, "hour": 10, "minute": 0}  # Monday
        self.area.save()

        # Create a Tuesday at 10:00
        test_time = timezone.now()
        days_ahead = 1 - test_time.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        test_time = test_time + timedelta(days=days_ahead)
        test_time = test_time.replace(hour=10, minute=0)

        self.assertFalse(should_trigger_timer(self.area, test_time))


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CheckTimerActionsTest(TestCase):
    """Test check_timer_actions task."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )

        self.service = Service.objects.create(
            name="Timer", description="Timer service", status=Service.Status.ACTIVE
        )

        self.action = Action.objects.create(
            service=self.service, name="timer_daily", description="Daily timer"
        )

        self.reaction = Reaction.objects.create(
            service=self.service, name="log_message", description="Log message"
        )

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_check_timer_actions_triggers_at_correct_time(self, mock_execute):
        """Test that timer triggers at configured time."""
        # Create area for 14:30
        area = Area.objects.create(
            owner=self.user,
            name="Daily 14:30",
            action=self.action,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        # Mock execute_reaction to prevent actual execution
        mock_execute.delay.return_value = MagicMock(id="task-123")

        # Run the task
        result = check_timer_actions()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["triggered"], 1)
        self.assertEqual(result["checked_areas"], 1)

        # Verify execution was created
        executions = Execution.objects.filter(area=area)
        self.assertEqual(executions.count(), 1)

    @freeze_time("2024-01-15 14:30:00")
    @patch("automations.tasks.execute_reaction")
    def test_check_timer_actions_idempotency(self, mock_execute):
        """Test that running twice at same time doesn't create duplicates."""
        # Create area for 14:30
        area = Area.objects.create(
            owner=self.user,
            name="Daily 14:30",
            action=self.action,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.ACTIVE,
        )

        # Mock execute_reaction
        mock_execute.delay.return_value = MagicMock(id="task-123")

        # Run task twice
        result1 = check_timer_actions()
        result2 = check_timer_actions()

        # First should trigger, second should skip
        self.assertEqual(result1["triggered"], 1)
        self.assertEqual(result2["triggered"], 0)
        self.assertEqual(result2["skipped"], 1)

        # Only one execution should exist
        self.assertEqual(Execution.objects.filter(area=area).count(), 1)

    def test_check_timer_actions_skips_disabled_areas(self):
        """Test that disabled areas are not processed."""
        Area.objects.create(
            owner=self.user,
            name="Disabled Area",
            action=self.action,
            reaction=self.reaction,
            action_config={"hour": 14, "minute": 30},
            status=Area.Status.DISABLED,  # Disabled
        )

        result = check_timer_actions()

        # Should not check disabled areas
        self.assertEqual(result["checked_areas"], 0)
        self.assertEqual(result["triggered"], 0)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ExecuteReactionTest(TestCase):
    """Test execute_reaction task."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )

        self.service = Service.objects.create(
            name="TestService", description="Test", status=Service.Status.ACTIVE
        )

        self.action = Action.objects.create(
            service=self.service, name="test_action", description="Test action"
        )

        self.reaction = Reaction.objects.create(
            service=self.service, name="log_message", description="Log message"
        )

        self.area = Area.objects.create(
            owner=self.user,
            name="Test Area",
            action=self.action,
            reaction=self.reaction,
            reaction_config={"message": "Test log"},
            status=Area.Status.ACTIVE,
        )

    def test_execute_reaction_success(self):
        """Test successful reaction execution."""
        # Create execution
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_event_001",
            status=Execution.Status.PENDING,
            trigger_data={"test": "data"},
        )

        # Execute reaction
        result = execute_reaction(execution.pk)

        # Verify result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["execution_id"], execution.pk)

        # Verify execution status updated
        execution.refresh_from_db()
        self.assertEqual(execution.status, Execution.Status.SUCCESS)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNotNone(execution.completed_at)

    def test_execute_reaction_nonexistent_execution(self):
        """Test handling of non-existent execution."""
        result = execute_reaction(99999)

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])

    @patch("automations.tasks._execute_reaction_logic")
    def test_execute_reaction_failure_and_retry(self, mock_logic):
        """Test reaction failure triggers retry."""
        # Make reaction logic fail
        mock_logic.side_effect = RuntimeError("Simulated failure")

        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_event_fail",
            status=Execution.Status.PENDING,
        )

        # Execute reaction (will retry in background)
        with self.assertRaises((RuntimeError, ValueError)):
            execute_reaction(execution.pk)

        # Verify execution marked as failed
        execution.refresh_from_db()
        self.assertEqual(execution.status, Execution.Status.FAILED)
        self.assertIn("Simulated failure", execution.error_message)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestExecutionFlowTest(TestCase):
    """Test the test_execution_flow task."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )

        service = Service.objects.create(
            name="TestService", description="Test", status=Service.Status.ACTIVE
        )

        action = Action.objects.create(
            service=service, name="test_action", description="Test"
        )

        reaction = Reaction.objects.create(
            service=service, name="log_message", description="Log"
        )

        self.area = Area.objects.create(
            owner=self.user,
            name="Test Area",
            action=action,
            reaction=reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("automations.tasks.execute_reaction")
    def test_test_execution_flow_success(self, mock_execute):
        """Test manual test execution flow."""
        # Mock execute_reaction to prevent actual execution
        mock_execute.delay.return_value = MagicMock(id="task-123")

        result = test_execution_flow(self.area.pk)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["area_id"], self.area.pk)
        self.assertIn("execution_id", result)

        # Verify execution was created
        execution = Execution.objects.get(pk=result["execution_id"])
        self.assertEqual(execution.area, self.area)
        self.assertTrue(execution.trigger_data.get("test"))

    def test_test_execution_flow_nonexistent_area(self):
        """Test handling of non-existent area."""
        result = test_execution_flow(99999)

        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"])
