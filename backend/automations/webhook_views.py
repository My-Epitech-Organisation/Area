"""
API views for webhook management.
"""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings

from users.permissions import IsAuthenticatedAndVerified

from .models import Service, WebhookSubscription
from .webhook_serializers import (
    WebhookStatusSerializer,
    WebhookSubscriptionListSerializer,
    WebhookSubscriptionSerializer,
)

logger = logging.getLogger(__name__)


class WebhookManagementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing webhook subscriptions.

    Provides endpoints to:
    - List user's webhook subscriptions
    - View webhook configuration status
    - Get recommendations for webhook vs polling
    """

    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = WebhookSubscriptionSerializer

    def get_queryset(self):
        """Return webhook subscriptions for the current user."""
        return WebhookSubscription.objects.filter(user=self.request.user).select_related(
            "service", "user"
        )

    @extend_schema(
        responses={200: WebhookSubscriptionListSerializer(many=True)},
        description="List all webhook subscriptions grouped by service",
    )
    @action(detail=False, methods=["get"])
    def by_service(self, request):
        """List webhook subscriptions grouped by service."""
        subscriptions = self.get_queryset()

        # Group by service
        services_data = {}
        for sub in subscriptions:
            service_name = sub.service.name
            if service_name not in services_data:
                services_data[service_name] = {
                    "service": service_name,
                    "subscriptions": [],
                    "total_count": 0,
                    "active_count": 0,
                }

            services_data[service_name]["subscriptions"].append(sub)
            services_data[service_name]["total_count"] += 1
            if sub.status == WebhookSubscription.Status.ACTIVE:
                services_data[service_name]["active_count"] += 1

        # Serialize
        serializer = WebhookSubscriptionListSerializer(
            list(services_data.values()), many=True
        )
        return Response(serializer.data)

    @extend_schema(
        responses={200: WebhookStatusSerializer()},
        description="Get webhook configuration status for a service",
    )
    @action(detail=False, methods=["get"], url_path=r"status/(?P<service_name>[^/.]+)")
    def status_for_service(self, request, service_name=None):
        """Get webhook configuration status for a specific service."""
        try:
            service = Service.objects.get(name=service_name)
        except Service.DoesNotExist:
            return Response(
                {"error": f"Service '{service_name}' not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check webhook configuration
        webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
        webhook_configured = bool(webhook_secrets.get(service_name))

        # Count active subscriptions
        active_subs = WebhookSubscription.objects.filter(
            user=request.user,
            service=service,
            status=WebhookSubscription.Status.ACTIVE,
        ).count()

        # Define supported events by service
        supported_events_map = {
            "github": ["issues", "pull_request", "push", "issue_comment", "star"],
            "twitch": [
                "stream.online",
                "stream.offline",
                "channel.follow",
                "channel.subscribe",
                "channel.update",
            ],
            "slack": ["message", "app_mention", "member_joined_channel"],
        }

        # Determine recommendation
        if webhook_configured:
            recommendation = f"✅ Webhooks enabled for {service_name}. Real-time events active."
        else:
            recommendation = f"⚠️ Configure webhooks for {service_name} for real-time events. Currently using polling."

        # Check if polling is enabled (by checking Celery Beat schedule)
        polling_tasks = {
            "github": "automations.check_github_actions",
            "twitch": "automations.check_twitch_actions",
            "slack": "automations.check_slack_actions",
        }
        
        polling_enabled = not webhook_configured  # Simplified check

        webhook_url = getattr(settings, "BACKEND_URL", "http://localhost:8080")
        full_webhook_url = f"{webhook_url}/webhooks/{service_name}/"

        data = {
            "service": service_name,
            "webhook_configured": webhook_configured,
            "webhook_url": full_webhook_url,
            "active_subscriptions": active_subs,
            "supported_events": supported_events_map.get(service_name, []),
            "polling_enabled": polling_enabled,
            "recommendation": recommendation,
        }

        serializer = WebhookStatusSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        responses={200: WebhookStatusSerializer(many=True)},
        description="Get webhook status for all services",
    )
    @action(detail=False, methods=["get"], url_path="status/all")
    def status_all(self, request):
        """Get webhook configuration status for all services."""
        services = ["github", "twitch", "slack"]
        results = []

        for service_name in services:
            response = self.status_for_service(request, service_name=service_name)
            if response.status_code == 200:
                results.append(response.data)

        return Response(results)
