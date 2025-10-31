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


class WebhookSubscription(models.Model):
    """
    Track active webhook subscriptions for users.

    ⚠️ SERVICE-SPECIFIC USAGE:

    - **Twitch EventSub**: REQUIRED - Twitch mandates explicit subscription management via API
    - **Slack**: OPTIONAL - Useful for tracking active event subscriptions
    - **GitHub**: NOT USED - Use GitHubAppInstallation instead (GitHub App handles webhooks automatically)

    This model is designed for services that require explicit webhook subscription
    management. For GitHub, the GitHubAppInstallation model provides automatic
    webhook configuration through the GitHub App.

    Key Features:
    - Track external subscription IDs (e.g., Twitch EventSub subscription ID)
    - Monitor subscription status and health
    - Store per-subscription configuration
    - Track event statistics (count, last received)
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending Verification"
        FAILED = "failed", "Failed"
        REVOKED = "revoked", "Revoked"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions",
    )

    # External subscription ID (for Twitch EventSub, etc.)
    external_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="External service's subscription ID (e.g., Twitch EventSub ID)",
    )

    # Event type being monitored
    event_type = models.CharField(
        max_length=100,
        help_text="Type of event (e.g., 'stream.online', 'issues', 'message')",
    )

    # Configuration for the webhook
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Webhook configuration (e.g., repository, channel, broadcaster_id)",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_event_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last received webhook event",
    )
    event_count = models.IntegerField(
        default=0,
        help_text="Total number of events received",
    )

    class Meta:
        verbose_name = "Webhook Subscription"
        verbose_name_plural = "Webhook Subscriptions"
        indexes = [
            models.Index(fields=["user", "service", "status"]),
            models.Index(fields=["external_subscription_id"]),
            models.Index(fields=["status", "updated_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "service", "event_type", "external_subscription_id"],
                name="unique_user_webhook_subscription",
            )
        ]

    def __str__(self):
        return f"{self.service.name}:{self.event_type} for {self.user.username}"

    def mark_active(self):
        """Mark webhook as active."""
        self.status = self.Status.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def mark_revoked(self):
        """Mark webhook as revoked."""
        self.status = self.Status.REVOKED
        self.save(update_fields=["status", "updated_at"])

    def record_event(self):
        """Record that an event was received."""
        from django.utils import timezone

        self.last_event_at = timezone.now()
        self.event_count += 1
        self.save(update_fields=["last_event_at", "event_count", "updated_at"])


class GitHubAppInstallation(models.Model):
    """
    Track GitHub App installations per user.

    ℹ️ GITHUB-SPECIFIC WEBHOOK MANAGEMENT:

    This model replaces the need for WebhookSubscription for GitHub services.
    When a user installs the AREA GitHub App on their account/organization,
    GitHub automatically configures webhooks for all selected repositories.

    Benefits vs manual webhook configuration:
    - ✅ No manual webhook setup required per repository
    - ✅ Automatic webhook configuration and signature validation
    - ✅ Centralized permission management via GitHub App
    - ✅ Tracks which repositories user has granted access to
    - ✅ Automatic updates when user adds/removes repositories

    Flow:
    1. User installs GitHub App via frontend banner
    2. GitHub sends installation webhook to our backend
    3. process_github_app_installation() creates/updates this record
    4. All repository webhooks are automatically configured by GitHub
    5. Webhook events arrive at /webhooks/github/ with automatic validation

    Related:
    - See github_app_views.py for installation API endpoints
    - See webhooks.py process_github_app_installation() for webhook handling
    """

    class AccountType(models.TextChoices):
        USER = "User", "User"
        ORGANIZATION = "Organization", "Organization"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_app_installations",
        help_text="AREA user who installed the app",
    )

    installation_id = models.BigIntegerField(
        unique=True, help_text="GitHub App installation ID"
    )

    account_login = models.CharField(
        max_length=255, help_text="GitHub username or organization name"
    )

    account_type = models.CharField(
        max_length=20, choices=AccountType.choices, default=AccountType.USER
    )

    # Repositories where app is installed (JSON list of full names)
    repositories = models.JSONField(
        default=list,
        blank=True,
        help_text="List of repo full names (e.g., ['owner/repo1', 'owner/repo2'])",
    )

    is_active = models.BooleanField(
        default=True, help_text="False if user uninstalled the app"
    )

    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "github_app_installations"
        indexes = [
            models.Index(fields=["user", "installation_id"]),
            models.Index(fields=["installation_id"]),
            models.Index(fields=["account_login"]),
        ]

    def __str__(self):
        return f"{self.account_login} (installation {self.installation_id})"

    def has_repository(self, repo_full_name: str) -> bool:
        """Check if app is installed on a specific repository."""
        return repo_full_name in self.repositories

    def add_repositories(self, repo_names: list[str]):
        """Add repositories to the installation."""
        self.repositories = list(set(self.repositories + repo_names))
        self.save(update_fields=["repositories", "updated_at"])

    def remove_repositories(self, repo_names: list[str]):
        """Remove repositories from the installation."""
        self.repositories = [r for r in self.repositories if r not in repo_names]
        self.save(update_fields=["repositories", "updated_at"])

    def deactivate(self):
        """Mark installation as inactive (uninstalled)."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
