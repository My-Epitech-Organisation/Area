"""
Tests for retry logic and monitoring features (Phase 5).
"""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from automations.models import Action, Area, Execution, Reaction, Service
from automations.tasks import (
    cleanup_old_executions,
    collect_execution_metrics,
    execute_reaction_task,
    send_to_dead_letter_queue,
)

User = get_user_model()


class ExecuteReactionRetryTest(TestCase):
    """Test execute_reaction_task retry behavior."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = Service.objects.create(
            name="test_service", description="Test Service"
        )
        self.action = Action.objects.create(
            service=self.service,
            name="test_action",
            description="Test Action",
        )
        self.reaction = Reaction.objects.create(
            service=self.service,
            name="test_reaction",
            description="Test Reaction",
        )
        self.area = Area.objects.create(
            name="Test Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            action_config={},
            reaction_config={},
        )
        self.execution = Execution.objects.create(
            area=self.area,
            trigger_data={"test": "data"},
            status="pending",
        )

    @patch("automations.tasks._execute_reaction_logic")
    def test_successful_execution_first_attempt(self, mock_logic):
        """Test successful execution on first attempt."""
        mock_logic.return_value = {"result": "success"}
        result = execute_reaction_task(self.execution.pk)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["retry_count"], 0)
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "success")
        mock_logic.assert_called_once()

    def test_execution_not_found(self):
        """Test handling of non-existent execution."""
        result = execute_reaction_task(99999)
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["message"].lower())


class DeadLetterQueueTest(TestCase):
    """Test dead letter queue handling."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = Service.objects.create(
            name="test_service", description="Test Service"
        )
        self.action = Action.objects.create(
            service=self.service,
            name="test_action",
            description="Test Action",
        )
        self.reaction = Reaction.objects.create(
            service=self.service,
            name="test_reaction",
            description="Test Reaction",
        )
        self.area = Area.objects.create(
            name="Test Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            action_config={},
            reaction_config={},
        )
        self.execution = Execution.objects.create(
            area=self.area,
            trigger_data={"test": "data"},
            status="failed",
        )

    def test_send_to_dlq_updates_execution(self):
        """Test DLQ handler updates execution status."""
        result = send_to_dead_letter_queue(
            execution_id=self.execution.pk,
            error="Test error",
            retry_count=3,
        )
        self.assertEqual(result["status"], "dlq_processed")
        self.assertEqual(result["execution_id"], self.execution.pk)
        self.execution.refresh_from_db()
        self.assertIn("dead letter queue", self.execution.error_message.lower())


class CollectExecutionMetricsTest(TestCase):
    """Test execution metrics collection."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = Service.objects.create(
            name="test_service", description="Test Service"
        )
        self.action = Action.objects.create(
            service=self.service,
            name="test_action",
            description="Test Action",
        )
        self.reaction = Reaction.objects.create(
            service=self.service,
            name="test_reaction",
            description="Test Reaction",
        )
        self.area = Area.objects.create(
            name="Test Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            action_config={},
            reaction_config={},
        )

    def test_metrics_collection_empty_database(self):
        """Test metrics collection with no executions."""
        metrics = collect_execution_metrics()
        self.assertIn("timestamp", metrics)
        self.assertIn("last_hour", metrics)
        self.assertEqual(metrics["last_hour"]["total_executions"], 0)


class CleanupOldExecutionsTest(TestCase):
    """Test cleanup of old executions."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.service = Service.objects.create(
            name="test_service", description="Test Service"
        )
        self.action = Action.objects.create(
            service=self.service,
            name="test_action",
            description="Test Action",
        )
        self.reaction = Reaction.objects.create(
            service=self.service,
            name="test_reaction",
            description="Test Reaction",
        )
        self.area = Area.objects.create(
            name="Test Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            action_config={},
            reaction_config={},
        )

    def test_cleanup_no_old_executions(self):
        """Test cleanup with no old executions."""
        now = timezone.now()
        Execution.objects.create(
            area=self.area,
            trigger_data={},
            status="success",
            created_at=now - timedelta(days=10),
        )
        result = cleanup_old_executions()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["deleted"]["total"], 0)

    def test_cleanup_old_successful_executions(self):
        """Test cleanup of old successful executions (>30 days)."""   
        from freezegun import freeze_time
        
        # Create execution 31 days ago
        past_date = timezone.now() - timedelta(days=31)
        with freeze_time(past_date):
            Execution.objects.create(
                area=self.area,
                trigger_data={},
                status="success",
            )
        
        result = cleanup_old_executions()
        self.assertEqual(result["deleted"]["successful"], 1)
        self.assertEqual(result["deleted"]["total"], 1)
