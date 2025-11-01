"""
Serializers for webhook management API.
"""

from rest_framework import serializers

from .models import WebhookSubscription


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for WebhookSubscription model."""

    service_name = serializers.CharField(source="service.name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = WebhookSubscription
        fields = [
            "id",
            "user",
            "username",
            "service",
            "service_name",
            "external_subscription_id",
            "event_type",
            "config",
            "status",
            "is_active",
            "created_at",
            "updated_at",
            "last_event_at",
            "event_count",
        ]
        read_only_fields = [
            "id",
            "username",
            "service_name",
            "created_at",
            "updated_at",
            "last_event_at",
            "event_count",
            "is_active",
        ]

    def get_is_active(self, obj):
        """Check if webhook subscription is active."""
        return obj.status == WebhookSubscription.Status.ACTIVE


class WebhookSubscriptionListSerializer(serializers.Serializer):
    """Serializer for listing webhook subscriptions by service."""

    service = serializers.CharField()
    subscriptions = WebhookSubscriptionSerializer(many=True, read_only=True)
    total_count = serializers.IntegerField()
    active_count = serializers.IntegerField()


class WebhookStatusSerializer(serializers.Serializer):
    """Serializer for webhook configuration status."""

    service = serializers.CharField()
    webhook_configured = serializers.BooleanField()
    webhook_url = serializers.URLField()
    active_subscriptions = serializers.IntegerField()
    supported_events = serializers.ListField(child=serializers.CharField())
    polling_enabled = serializers.BooleanField()
    recommendation = serializers.CharField()
