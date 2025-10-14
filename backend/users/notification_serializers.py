"""Serializers for OAuth notifications."""

from rest_framework import serializers

from users.models import OAuthNotification


class OAuthNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for OAuth notifications.

    Provides read-only access to notification details for API consumers.
    """

    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )
    time_since_created = serializers.SerializerMethodField()

    class Meta:
        model = OAuthNotification
        fields = [
            "id",
            "service_name",
            "notification_type",
            "notification_type_display",
            "message",
            "is_read",
            "is_resolved",
            "created_at",
            "resolved_at",
            "time_since_created",
        ]
        read_only_fields = ["id", "created_at", "resolved_at"]

    def get_time_since_created(self, obj) -> str:
        """
        Get human-readable time since notification was created.

        Returns:
            str: Human-readable time delta (e.g., "5 minutes ago")
        """
        from datetime import timedelta

        from django.utils import timezone

        delta = timezone.now() - obj.created_at

        if delta < timedelta(minutes=1):
            return "just now"
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta < timedelta(days=30):
            days = delta.days
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"


class OAuthNotificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating OAuth notification status.

    Allows users to mark notifications as read or resolved.
    """

    class Meta:
        model = OAuthNotification
        fields = ["is_read", "is_resolved"]

    def validate(self, attrs):
        """Validate update data."""
        # Allow unresolving notifications (no restriction)
        return attrs

    def update(self, instance, validated_data):
        """Update notification and set resolved_at timestamp."""
        from django.utils import timezone

        if validated_data.get("is_resolved") and not instance.is_resolved:
            validated_data["resolved_at"] = timezone.now()

        return super().update(instance, validated_data)
