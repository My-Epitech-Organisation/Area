from django.contrib import admin

from .models import Action, Area, Execution, Reaction, Service, WebhookSubscription


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
