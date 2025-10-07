"""Serializers for OAuth2 authentication and service connection management."""

from rest_framework import serializers

from django.utils import timezone

from .models import ServiceToken


class ServiceTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for user's connected service tokens.

    Provides read-only access to service connection status with
    computed fields for expiration information.
    """

    is_expired = serializers.SerializerMethodField()
    expires_in_minutes = serializers.SerializerMethodField()
    has_refresh_token = serializers.SerializerMethodField()

    class Meta:
        model = ServiceToken
        fields = [
            "service_name",
            "created_at",
            "expires_at",
            "is_expired",
            "expires_in_minutes",
            "has_refresh_token",
        ]
        read_only_fields = fields

    def get_is_expired(self, obj: ServiceToken) -> bool:
        """Check if token is expired."""
        if not obj.expires_at:
            return False
        return timezone.now() >= obj.expires_at

    def get_expires_in_minutes(self, obj: ServiceToken) -> int | None:
        """Calculate minutes until expiration."""
        if not obj.expires_at:
            return None

        delta = obj.expires_at - timezone.now()
        minutes = int(delta.total_seconds() / 60)
        return max(0, minutes)  # Don't return negative values

    def get_has_refresh_token(self, obj: ServiceToken) -> bool:
        """Check if refresh token is available."""
        return bool(obj.refresh_token)


class OAuthInitiateResponseSerializer(serializers.Serializer):
    """
    Response serializer for OAuth2 initiation.

    Returns the authorization URL and state for CSRF protection.
    """

    redirect_url = serializers.URLField(
        help_text="URL to redirect user to for authorization"
    )
    state = serializers.CharField(help_text="CSRF protection state parameter")
    provider = serializers.CharField(help_text="OAuth2 provider name")
    expires_in = serializers.IntegerField(
        help_text="State expiry time in seconds", default=600
    )


class OAuthCallbackSerializer(serializers.Serializer):
    """
    Validation serializer for OAuth2 callback parameters.

    Validates the authorization code and state from the OAuth2 provider.
    """

    code = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Authorization code from OAuth2 provider",
    )
    state = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="CSRF protection state parameter",
    )
    error = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Error code if authorization failed",
    )
    error_description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Human-readable error description",
    )

    def validate(self, attrs):
        """Validate that either code or error is present."""
        has_code = bool(attrs.get("code"))
        has_error = bool(attrs.get("error"))

        if not has_code and not has_error:
            raise serializers.ValidationError(
                "Either 'code' or 'error' parameter must be provided"
            )

        if has_code and not attrs.get("state"):
            raise serializers.ValidationError(
                "'state' parameter is required when 'code' is present"
            )

        return attrs


class ServiceConnectionListSerializer(serializers.Serializer):
    """
    Serializer for listing available and connected services.

    Provides overview of OAuth2 integration status.
    """

    connected_services = ServiceTokenSerializer(many=True, read_only=True)
    available_providers = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
    total_connected = serializers.IntegerField(read_only=True)


class ServiceDisconnectSerializer(serializers.Serializer):
    """Response serializer for service disconnection."""

    message = serializers.CharField(read_only=True)
    service = serializers.CharField(read_only=True)
    revoked_at_provider = serializers.BooleanField(read_only=True)
