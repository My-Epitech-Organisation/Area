from django.contrib import admin

from .models import (
    Action,
    Area,
    Execution,
    GitHubAppInstallation,
    NotionPage,
    NotionWebhookSubscription,
    Reaction,
    Service,
    WebhookSubscription,
)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin configuration for Service model."""

    list_display = ("name", "description", "status")
    list_filter = ("status",)
    search_fields = ("name", "description")
    list_per_page = 20

    fieldsets = (
        ("Service Information", {"fields": ("name", "description", "status")}),
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """Admin configuration for Action model."""

    list_display = ("name", "service", "description")
    list_filter = ("service",)
    search_fields = ("name", "description", "service__name")
    list_per_page = 25

    fieldsets = (
        ("Action Information", {"fields": ("service", "name", "description")}),
    )


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    """Admin configuration for Reaction model."""

    list_display = ("name", "service", "description")
    list_filter = ("service",)
    search_fields = ("name", "description", "service__name")
    list_per_page = 25

    fieldsets = (
        ("Reaction Information", {"fields": ("service", "name", "description")}),
    )


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """Admin configuration for Area model."""

    list_display = ("name", "owner", "action", "reaction", "status", "created_at")

    list_filter = ("status", "action__service", "reaction__service", "created_at")

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
        "action__name",
        "reaction__name",
    )

    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        ("Basic Information", {"fields": ("name", "owner", "status")}),
        ("Action Configuration", {"fields": ("action", "action_config")}),
        ("Reaction Configuration", {"fields": ("reaction", "reaction_config")}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at",)


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    """Admin configuration for Execution model."""

    list_display = (
        "id",
        "area",
        "status",
        "external_event_id",
        "created_at",
        "duration_display",
        "retry_count",
    )

    list_filter = (
        "status",
        "created_at",
        "area__action__service",
        "area__reaction__service",
    )

    search_fields = (
        "external_event_id",
        "area__name",
        "area__owner__username",
        "error_message",
    )

    date_hierarchy = "created_at"
    list_per_page = 50

    fieldsets = (
        (
            "Execution Information",
            {
                "fields": (
                    "area",
                    "external_event_id",
                    "status",
                    "retry_count",
                )
            },
        ),
        (
            "Timing",
            {
                "fields": ("created_at", "started_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "Data",
            {
                "fields": ("trigger_data", "result_data"),
                "classes": ("collapse",),
            },
        ),
        (
            "Error Information",
            {
                "fields": ("error_message",),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = (
        "area",
        "external_event_id",
        "status",
        "created_at",
        "started_at",
        "completed_at",
        "trigger_data",
        "result_data",
        "error_message",
        "retry_count",
    )

    def duration_display(self, obj):
        """Display execution duration in a human-readable format."""
        duration = obj.duration
        if duration is None:
            return "-"
        if duration < 1:
            return f"{duration * 1000:.0f}ms"
        return f"{duration:.2f}s"

    duration_display.short_description = "Duration"

    def has_add_permission(self, request):
        """Disable manual creation of executions in admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only allow deletion of old/completed executions."""
        # Allow superusers to delete anything
        if request.user.is_superuser:
            return True
        # Only allow deletion of terminal executions
        return bool(obj and obj.is_terminal)


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for WebhookSubscription model."""

    list_display = (
        "id",
        "user",
        "service",
        "event_type",
        "status",
        "event_count",
        "last_event_at",
        "created_at",
    )
    list_filter = ("service", "status", "event_type")
    search_fields = (
        "user__username",
        "user__email",
        "service__name",
        "event_type",
        "external_subscription_id",
    )
    readonly_fields = ("created_at", "updated_at", "event_count", "last_event_at")
    list_per_page = 25

    fieldsets = (
        (
            "Subscription Information",
            {
                "fields": (
                    "user",
                    "service",
                    "event_type",
                    "external_subscription_id",
                    "status",
                )
            },
        ),
        ("Configuration", {"fields": ("config",)}),
        (
            "Statistics",
            {
                "fields": (
                    "event_count",
                    "last_event_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        """Webhook subscriptions are managed programmatically."""
        return request.user.is_superuser


@admin.register(GitHubAppInstallation)
class GitHubAppInstallationAdmin(admin.ModelAdmin):
    """Admin configuration for GitHubAppInstallation model."""

    list_display = (
        "id",
        "user",
        "account_login",
        "account_type",
        "installation_id",
        "is_active",
        "repository_count",
        "installed_at",
    )
    list_filter = ("account_type", "is_active", "installed_at")
    search_fields = (
        "user__username",
        "user__email",
        "account_login",
        "installation_id",
    )
    readonly_fields = (
        "installation_id",
        "installed_at",
        "updated_at",
        "repository_count",
    )
    list_per_page = 25

    fieldsets = (
        (
            "Installation Information",
            {
                "fields": (
                    "user",
                    "installation_id",
                    "account_login",
                    "account_type",
                    "is_active",
                )
            },
        ),
        ("Repositories", {"fields": ("repositories", "repository_count")}),
        ("Timestamps", {"fields": ("installed_at", "updated_at")}),
    )

    def repository_count(self, obj):
        """Display the number of repositories."""
        return len(obj.repositories) if obj.repositories else 0

    repository_count.short_description = "Repository Count"  # type: ignore

    def has_add_permission(self, request):
        """GitHub App installations are managed via webhooks."""
        return False


@admin.register(NotionPage)
class NotionPageAdmin(admin.ModelAdmin):
    """Admin configuration for NotionPage model."""

    list_display = (
        "id",
        "user",
        "title",
        "page_type",
        "workspace_id",
        "is_accessible",
        "updated_at",
    )
    list_filter = ("page_type", "is_accessible", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "title",
        "page_id",
        "workspace_id",
    )
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50

    fieldsets = (
        (
            "Page Information",
            {
                "fields": (
                    "user",
                    "page_id",
                    "page_type",
                    "title",
                    "workspace_id",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "icon",
                    "parent",
                    "url",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_accessible",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize query with select_related."""
        return super().get_queryset(request).select_related("user")


@admin.register(NotionWebhookSubscription)
class NotionWebhookSubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for NotionWebhookSubscription model."""

    list_display = (
        "id",
        "user",
        "webhook_id",
        "workspace_id",
        "target_display",
        "status",
        "event_count",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "webhook_id",
        "workspace_id",
        "page_id",
        "database_id",
    )
    readonly_fields = (
        "webhook_id",
        "workspace_id",
        "created_at",
        "updated_at",
        "event_count",
        "last_event_at",
    )
    list_per_page = 25

    fieldsets = (
        (
            "Webhook Information",
            {
                "fields": (
                    "user",
                    "webhook_id",
                    "workspace_id",
                    "status",
                )
            },
        ),
        (
            "Target",
            {
                "fields": ("page_id", "database_id", "event_types"),
                "description": "The Notion page or database being monitored",
            },
        ),
        (
            "Statistics",
            {"fields": ("event_count", "last_event_at", "created_at", "updated_at")},
        ),
    )

    def target_display(self, obj):
        """Display the target (page or database) being monitored."""
        if obj.page_id:
            return f"Page: {obj.page_id[:16]}..."
        elif obj.database_id:
            return f"Database: {obj.database_id[:16]}..."
        return "Workspace"

    target_display.short_description = "Target"  # type: ignore

    def has_add_permission(self, request):
        """Notion webhooks are managed via API."""
        return False
