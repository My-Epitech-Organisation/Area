"""Serializers for password reset functionality."""

from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import PasswordResetToken

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for requesting a password reset."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate that the email exists in the system."""
        # Normalize email
        value = value.lower().strip()

        # Check if user exists (but don't reveal this to prevent user enumeration)
        # We'll handle this in the view
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password with a token."""

    token = serializers.CharField(required=True, max_length=64)
    new_password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Validate that passwords match and token is valid."""
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        # Check passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )

        # Validate token exists and is valid
        token = attrs.get("token")
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid():
                raise serializers.ValidationError(
                    {"token": "Token has expired or has already been used"}
                )
            attrs["reset_token"] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token"}) from None

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password when authenticated."""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """Validate that the old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )

        return attrs
