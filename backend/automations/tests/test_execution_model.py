"""
Unit tests for the Execution model.

Tests cover:
- Model creation and field validation
- Idempotency constraint (unique external_event_id per area)
- Status transitions (pending -> running -> success/failed)
- Helper methods (mark_started, mark_success, mark_failed, mark_skipped)
- Properties (duration, is_terminal)
"""

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from automations.models import Action, Area, Execution, Reaction, Service
from users.models import User


class ExecutionModelTest(TestCase):
    """Test cases for Execution model."""

    def setUp(self):
        """Set up test data for all test methods."""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create test service
        self.service = Service.objects.create(
            name="TestService",
            description="Test service for executions",
            status=Service.Status.ACTIVE,
        )

        # Create test action
        self.action = Action.objects.create(
            service=self.service,
            name="test_action",
            description="Test action",
        )

        # Create test reaction
        self.reaction = Reaction.objects.create(
            service=self.service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create test area
        self.area = Area.objects.create(
            owner=self.user,
            name="Test Area",
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    def test_execution_creation(self):
        """Test creating a basic execution."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_event_001",
            trigger_data={"test": "data"},
        )

        self.assertEqual(execution.area, self.area)
        self.assertEqual(execution.external_event_id, "test_event_001")
        self.assertEqual(execution.status, Execution.Status.PENDING)
        self.assertEqual(execution.trigger_data, {"test": "data"})
        self.assertEqual(execution.retry_count, 0)
        self.assertIsNotNone(execution.created_at)
        self.assertIsNone(execution.started_at)
        self.assertIsNone(execution.completed_at)

    def test_execution_idempotency_constraint(self):
        """Test that duplicate external_event_id for same area raises error."""
        # Create first execution
        Execution.objects.create(
            area=self.area,
            external_event_id="duplicate_event",
        )

        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Execution.objects.create(
                area=self.area,
                external_event_id="duplicate_event",
            )

    def test_execution_same_event_different_area(self):
        """Test that same external_event_id is allowed for different areas."""
        # Create another area
        area2 = Area.objects.create(
            owner=self.user,
            name="Test Area 2",
            action=self.action,
            reaction=self.reaction,
        )

        # Create executions with same event_id but different areas
        exec1 = Execution.objects.create(
            area=self.area,
            external_event_id="shared_event",
        )

        exec2 = Execution.objects.create(
            area=area2,
            external_event_id="shared_event",
        )

        # Both should exist
        self.assertIsNotNone(exec1.id)
        self.assertIsNotNone(exec2.id)
        self.assertNotEqual(exec1.id, exec2.id)

    def test_mark_started(self):
        """Test marking execution as started."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_start",
        )

        self.assertEqual(execution.status, Execution.Status.PENDING)
        self.assertIsNone(execution.started_at)

        execution.mark_started()

        self.assertEqual(execution.status, Execution.Status.RUNNING)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNone(execution.completed_at)

    def test_mark_success(self):
        """Test marking execution as successful."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_success",
        )

        execution.mark_started()
        result_data = {"result": "success", "output": "test"}
        execution.mark_success(result_data)

        self.assertEqual(execution.status, Execution.Status.SUCCESS)
        self.assertIsNotNone(execution.completed_at)
        self.assertEqual(execution.result_data, result_data)

    def test_mark_failed(self):
        """Test marking execution as failed."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_failure",
        )

        execution.mark_started()
        error_message = "Connection timeout"
        execution.mark_failed(error_message)

        self.assertEqual(execution.status, Execution.Status.FAILED)
        self.assertIsNotNone(execution.completed_at)
        self.assertEqual(execution.error_message, error_message)

    def test_mark_skipped(self):
        """Test marking execution as skipped."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_skip",
        )

        reason = "Area is disabled"
        execution.mark_skipped(reason)

        self.assertEqual(execution.status, Execution.Status.SKIPPED)
        self.assertIsNotNone(execution.completed_at)
        self.assertEqual(execution.error_message, reason)

    def test_duration_property(self):
        """Test duration calculation."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_duration",
        )

        # No duration before started
        self.assertIsNone(execution.duration)

        # Mark started
        execution.mark_started()
        self.assertIsNone(execution.duration)  # Still None (not completed)

        # Mark success - should have duration
        execution.mark_success()
        duration = execution.duration

        self.assertIsNotNone(duration)
        self.assertIsInstance(duration, float)
        self.assertGreaterEqual(duration, 0)

    def test_is_terminal_property(self):
        """Test is_terminal property for different statuses."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_terminal",
        )

        # Pending - not terminal
        self.assertFalse(execution.is_terminal)

        # Running - not terminal
        execution.mark_started()
        self.assertFalse(execution.is_terminal)

        # Success - terminal
        execution.status = Execution.Status.SUCCESS
        execution.save()
        self.assertTrue(execution.is_terminal)

        # Failed - terminal
        execution2 = Execution.objects.create(
            area=self.area,
            external_event_id="test_terminal_2",
        )
        execution2.mark_failed("Test error")
        self.assertTrue(execution2.is_terminal)

        # Skipped - terminal
        execution3 = Execution.objects.create(
            area=self.area,
            external_event_id="test_terminal_3",
        )
        execution3.mark_skipped()
        self.assertTrue(execution3.is_terminal)

    def test_execution_string_representation(self):
        """Test __str__ method."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_str",
        )

        str_repr = str(execution)
        self.assertIn(str(execution.pk), str_repr)
        self.assertIn(self.area.name, str_repr)
        self.assertIn(execution.status, str_repr)

    def test_execution_ordering(self):
        """Test that executions are ordered by created_at descending."""
        # Create multiple executions
        exec1 = Execution.objects.create(
            area=self.area,
            external_event_id="event_1",
        )

        exec2 = Execution.objects.create(
            area=self.area,
            external_event_id="event_2",
        )

        exec3 = Execution.objects.create(
            area=self.area,
            external_event_id="event_3",
        )

        # Get all executions (should be in reverse chronological order)
        executions = list(Execution.objects.all())

        self.assertEqual(executions[0], exec3)  # Most recent first
        self.assertEqual(executions[1], exec2)
        self.assertEqual(executions[2], exec1)

    def test_retry_count_increment(self):
        """Test incrementing retry_count."""
        execution = Execution.objects.create(
            area=self.area,
            external_event_id="test_retry",
        )

        self.assertEqual(execution.retry_count, 0)

        # Simulate retries
        execution.retry_count += 1
        execution.save()
        self.assertEqual(execution.retry_count, 1)

        execution.retry_count += 1
        execution.save()
        self.assertEqual(execution.retry_count, 2)
