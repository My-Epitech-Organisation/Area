from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import OAuthNotification, ServiceToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""

    # Fields to display in the user list (email first as it's the primary identifier)
    list_display = (
        "email",
        "username",
        "email_verified",
        "is_staff",
        "is_active",
        "date_joined",
    )

    # Filters for the right sidebar
    list_filter = (
        "email_verified",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    # Fields to search (email first as it's the primary identifier)
    search_fields = ("email", "username", "first_name", "last_name")

    # Use email for ordering
    ordering = ("email",)

    # Add custom fields to the user edit form
    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (
            "Email Verification",
            {"fields": ("email_verified", "email_verification_token")},
        ),
    ]

    # Make email_verification_token read-only for security
    readonly_fields = ("email_verification_token",)


@admin.register(ServiceToken)
class ServiceTokenAdmin(admin.ModelAdmin):
    """Admin configuration for ServiceToken model."""

    list_display = ("user", "service_name", "expires_at", "created_at")

    list_filter = ("service_name", "created_at", "expires_at")

    search_fields = ("user__email", "user__username", "service_name")

    # Make tokens read-only for security
    readonly_fields = ("access_token", "refresh_token", "created_at")

    # Group fields logically
    fieldsets = (
        ("Service Information", {"fields": ("user", "service_name")}),
        ("Tokens", {"fields": ("access_token", "refresh_token", "expires_at")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )


@admin.register(OAuthNotification)
class OAuthNotificationAdmin(admin.ModelAdmin):
    """Admin configuration for OAuthNotification model."""

    list_display = (
        "user",
        "service_name",
        "notification_type",
        "status_badge",
        "created_at",
        "resolved_at",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "is_resolved",
        "service_name",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
        "service_name",
        "message",
    )

    readonly_fields = ("created_at", "resolved_at")

    actions = ["mark_as_read", "mark_as_resolved"]

    # Group fields logically
    fieldsets = (
        (
            "Notification Details",
            {
                "fields": (
                    "user",
                    "service_name",
                    "notification_type",
                    "message",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "is_resolved",
                    "created_at",
                    "resolved_at",
                )
            },
        ),
    )

    def status_badge(self, obj):
        """Display colored status badge."""
        if obj.is_resolved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Resolved</span>'
            )
        elif obj.is_read:
            return format_html(
                '<span style="color: orange; font-weight: bold;">○ Read</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">● Unread</span>'
            )

    status_badge.short_description = "Status"

    @admin.action(description="Mark selected notifications as read")
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")

    @admin.action(description="Mark selected notifications as resolved")
    def mark_as_resolved(self, request, queryset):
        """Mark selected notifications as resolved."""
        from django.utils import timezone

        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f"{updated} notifications marked as resolved.")
