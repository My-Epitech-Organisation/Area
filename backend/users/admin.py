from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ServiceToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""

    # Fields to display in the user list
    list_display = (
        "username",
        "email",
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

    # Fields to search
    search_fields = ("username", "email", "first_name", "last_name")

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

    search_fields = ("user__username", "user__email", "service_name")

    # Make tokens read-only for security
    readonly_fields = ("access_token", "refresh_token", "created_at")

    # Group fields logically
    fieldsets = (
        ("Service Information", {"fields": ("user", "service_name")}),
        ("Tokens", {"fields": ("access_token", "refresh_token", "expires_at")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
