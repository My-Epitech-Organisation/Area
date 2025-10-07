##
## EPITECH PROJECT, 2025
## Area
## File description:
## serializers
##

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm password"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "email_verified")
        read_only_fields = ("email_verified",)
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": False},  # Username is now optional (display name)
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        # Validate password strength
        try:
            validate_password(attrs["password"], self.instance)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        # Mark email as unverified by default
        user.email_verified = False
        user.save()
        return user


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True, help_text="Google ID token from mobile app")


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that uses email for authentication.

    Since our User model now uses email as USERNAME_FIELD, we override to accept
    'email' in the input and map it to the 'username' field expected by SimpleJWT.
    """

    username_field = "email"  # Tell DRF to use 'email' as the input field name

    def validate(self, attrs):  # type: ignore[override]
        # Map 'email' from attrs to 'username' for parent validation
        # since SimpleJWT expects 'username' internally but our USERNAME_FIELD is 'email'
        if "email" in attrs:
            attrs[User.USERNAME_FIELD] = attrs.pop("email")

        return super().validate(attrs)
