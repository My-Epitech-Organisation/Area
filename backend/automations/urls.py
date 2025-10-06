"""
URL routing for the AREA automation API.

This module defines the API endpoints for:
- Service discovery
- Action/Reaction discovery
- Area CRUD operations
- About.json endpoint
- Webhook receiver
"""

from rest_framework.routers import DefaultRouter

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
    # API endpoints
    path("api/", include(router.urls)),
    # Special endpoint for service discovery
    path("about.json", views.about_json_view, name="about"),
    # Webhook receiver endpoint
    path("webhooks/<str:service>/", webhook_receiver, name="webhook-receiver"),
]
