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
    # Schema endpoints
    path(
        "api/schemas/actions/<str:pk>/",
        views.ActionSchemaView.as_view({"get": "retrieve"}),
        name="action-schema",
    ),
    path(
        "api/schemas/reactions/<str:pk>/",
        views.ReactionSchemaView.as_view({"get": "retrieve"}),
        name="reaction-schema",
    ),
    # Special endpoint for service discovery
    path("about.json", views.about_json_view, name="about"),
    # Webhook receiver endpoint
    path("webhooks/<str:service>/", webhook_receiver, name="webhook-receiver"),
]
