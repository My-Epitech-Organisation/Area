from django.contrib import admin

from .models import Action, Area, Reaction, Service


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
