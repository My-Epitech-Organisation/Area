from django.conf import settings
from django.db import models


class Service(models.Model):
    """
    Represents an available external service (e.g., GitHub, Gmail).
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    def __str__(self):
        return self.name


class Action(models.Model):
    """
    Represents a possible trigger from a service.
    """

    service = models.ForeignKey(
        Service, related_name="actions", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    config_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON schema defining required configuration fields for this action",
    )

    def __str__(self):
        return f"{self.service.name}: {self.name}"


class Reaction(models.Model):
    """
    Represents a possible reaction to perform on a service.
    """

    service = models.ForeignKey(
        Service, related_name="reactions", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    config_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON schema defining required configuration fields for this reaction",
    )

    def __str__(self):
        return f"{self.service.name}: {self.name}"


class Area(models.Model):
    """
    Represents a user-defined automation linking an Action to a Reaction.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        PAUSED = "paused", "Paused"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    action_config = models.JSONField(default=dict, blank=True)
    reaction_config = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"'{self.name}' for {self.owner.username}"


class Execution(models.Model):
    """
    Represents a single execution of an AREA automation.

    Tracks when an Action was triggered and the resulting Reaction execution,
    including status, timing, and any errors encountered.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    # Core relationships
    area = models.ForeignKey(Area, related_name="executions", on_delete=models.CASCADE)

    # Idempotency key - prevents duplicate executions for the same external event
    external_event_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text=(
            "Unique identifier for the external event "
            "(e.g., webhook event ID, timer timestamp)"
        ),
    )

    # Execution status and timing
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the execution was created"
    )
    started_at = models.DateTimeField(
        null=True, blank=True, help_text="When the execution actually started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the execution completed (success or failed)",
    )

    # Execution data
    trigger_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data from the trigger/action that initiated this execution",
    )
    result_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Result data from the reaction execution",
    )
    error_message = models.TextField(
        blank=True, default="", help_text="Error message if execution failed"
    )

    # Retry tracking
    retry_count = models.IntegerField(
        default=0, help_text="Number of times this execution has been retried"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["area", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
        # Ensure idempotency: same area + external_event_id = unique execution
        constraints = [
            models.UniqueConstraint(
                fields=["area", "external_event_id"],
                name="unique_area_external_event",
            )
        ]

    def __str__(self):
        pk = self.pk if self.pk else "new"
        return f"Execution #{pk} - {self.area.name} ({self.status})"

    def mark_started(self):
        """Mark execution as started."""
        from django.utils import timezone

        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at"])

    def mark_success(self, result_data=None):
        """Mark execution as successful."""
        from django.utils import timezone

        self.status = self.Status.SUCCESS
        self.completed_at = timezone.now()
        if result_data:
            self.result_data = result_data
        self.save(update_fields=["status", "completed_at", "result_data"])

    def mark_failed(self, error_message):
        """Mark execution as failed."""
        from django.utils import timezone

        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=["status", "completed_at", "error_message"])

    def mark_skipped(self, reason=""):
        """Mark execution as skipped."""
        from django.utils import timezone

        self.status = self.Status.SKIPPED
        self.completed_at = timezone.now()
        if reason:
            self.error_message = reason
        self.save(update_fields=["status", "completed_at", "error_message"])

    @property
    def duration(self):
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_terminal(self):
        """Check if execution is in a terminal state."""
        return self.status in [
            self.Status.SUCCESS,
            self.Status.FAILED,
            self.Status.SKIPPED,
        ]


class ActionState(models.Model):
    """
    Stores the last check state for polling-based actions.

    This model is used to track when an action was last checked and what
    the last processed event was, preventing duplicate processing and
    enabling incremental polling.

    For example, for GitHub actions:
    - last_checked_at: When we last polled the GitHub API
    - last_event_id: ID of the last processed issue/PR
    - metadata: Additional state data (e.g., ETag for conditional requests)
    """

    area = models.OneToOneField(
        Area,
        on_delete=models.CASCADE,
        related_name="action_state",
        help_text="The Area this state belongs to",
    )

    last_checked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last successful check",
    )

    last_event_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="ID of the last processed event (issue ID, commit SHA, etc.)",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional state data (ETags, cursor tokens, etc.)",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Action State"
        verbose_name_plural = "Action States"
        indexes = [
            models.Index(fields=["last_checked_at"]),
        ]

    def __str__(self):
        return f"State for Area #{self.area.id} ({self.area.action.name})"
