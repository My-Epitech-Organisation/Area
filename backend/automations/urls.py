##
## EPITECH PROJECT, 2025
## Area
## File description:
## urls
##

"""
URL routing for the AREA automation API.

This module defines the API endpoints for:
- Service discovery
- Action/Reaction discovery
- Area CRUD operations
- About.json endpoint
- Webhook receiver
"""

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import include, path

from . import github_app_views, notion_pages_views, notion_webhook_views, views
from .webhooks import webhook_receiver

# Create router and register viewsets
router = DefaultRouter()
router.register(r"services", views.ServiceViewSet, basename="service")
router.register(r"actions", views.ActionViewSet, basename="action")
router.register(r"reactions", views.ReactionViewSet, basename="reaction")
router.register(r"areas", views.AreaViewSet, basename="area")
router.register(r"executions", views.ExecutionViewSet, basename="execution")

# Import webhook views
try:
    from . import webhook_views

    router.register(
        r"webhooks/manage", webhook_views.WebhookManagementViewSet, basename="webhook"
    )
except ImportError:
    pass  # webhook_views may not be available yet

app_name = "automations"

urlpatterns = [
    # JWT authentication endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API schema and documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="automations:schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="automations:schema"),
        name="redoc",
    ),
    # API endpoints
    path("api/", include(router.urls)),
    # Special endpoint for service discovery
    path("about.json", views.about_json_view, name="about"),
    # Logo proxy endpoint
    path("logos/<str:service>/", views.logo_proxy_view, name="logo-proxy"),
    # Webhook receiver endpoint
    path("webhooks/<str:service>/", webhook_receiver, name="webhook-receiver"),
    # GitHub App endpoints
    path(
        "api/github-app/status/",
        github_app_views.github_app_status,
        name="github-app-status",
    ),
    path(
        "api/github-app/link-installation/",
        github_app_views.github_app_link_installation,
        name="github-app-link",
    ),
    path(
        "api/github-app/repositories/",
        github_app_views.github_app_repositories,
        name="github-app-repos",
    ),
    # Notion Webhook endpoints
    path(
        "api/notion-webhooks/status/",
        notion_webhook_views.notion_webhook_status,
        name="notion-webhook-status",
    ),
    path(
        "api/notion-webhooks/create/",
        notion_webhook_views.notion_webhook_create,
        name="notion-webhook-create",
    ),
    path(
        "api/notion-webhooks/<str:webhook_id>/delete/",
        notion_webhook_views.notion_webhook_delete,
        name="notion-webhook-delete",
    ),
    path(
        "api/notion-webhooks/list/",
        notion_webhook_views.notion_webhook_list,
        name="notion-webhook-list",
    ),
    # Notion Pages endpoints (for GitHub App-like UX)
    path(
        "api/notion-pages/",
        notion_pages_views.notion_pages_list,
        name="notion-pages-list",
    ),
    path(
        "api/notion-pages/refresh/",
        notion_pages_views.notion_pages_refresh,
        name="notion-pages-refresh",
    ),
    # Debug endpoints
    path(
        "api/debug/trigger/<int:area_id>/",
        views.DebugTriggerView.as_view({"post": "create"}),
        name="debug-trigger",
    ),
    path(
        "api/debug/executions/<int:area_id>/",
        views.DebugExecutionsView.as_view({"get": "list"}),
        name="debug-executions",
    ),
]
