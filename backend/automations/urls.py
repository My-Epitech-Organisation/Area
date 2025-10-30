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

from . import views
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
    router.register(r"webhooks/manage", webhook_views.WebhookManagementViewSet, basename="webhook")
except ImportError:
    pass  # webhook_views may not be available yet

# Import GitHub App views
from . import github_app_views

# Import Twitch EventSub views
from . import twitch_eventsub_views

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
    path("api/github-app/status/", github_app_views.github_app_status, name="github-app-status"),
    path("api/github-app/link-installation/", github_app_views.github_app_link_installation, name="github-app-link"),
    path("api/github-app/repositories/", github_app_views.github_app_repositories, name="github-app-repos"),
    # Twitch EventSub endpoints
    path("api/twitch-eventsub/status/", twitch_eventsub_views.twitch_eventsub_status, name="twitch-eventsub-status"),
    path("api/twitch-eventsub/subscribe/", twitch_eventsub_views.twitch_eventsub_subscribe, name="twitch-eventsub-subscribe"),
    path("api/twitch-eventsub/unsubscribe/<int:subscription_id>/", twitch_eventsub_views.twitch_eventsub_unsubscribe, name="twitch-eventsub-unsubscribe"),
    path("api/twitch-eventsub/delete-all/", twitch_eventsub_views.twitch_eventsub_delete_all, name="twitch-eventsub-delete-all"),
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
