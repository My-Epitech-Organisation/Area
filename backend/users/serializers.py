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
        extra_kwargs = {"email": {"required": True}}

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


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that allows authentication with username OR email.

    The incoming credential can be supplied in either the 'username' field (default SimpleJWT
    expectation) or an 'email' field. If the value contains an '@', we first try to match
    against the email field; otherwise we attempt username. Case-insensitive lookups are used.
    """

    def validate(self, attrs):  # type: ignore[override]
        # Original input before parent validation may normalize username
        login_value = attrs.get("username") or self.initial_data.get("email") or ""
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()

        candidate_user = None

        # Try email if it looks like one
        if "@" in login_value:
            try:
                candidate_user = UserModel.objects.get(email__iexact=login_value)
            except UserModel.DoesNotExist:
                candidate_user = None

        # Fallback to username
        if candidate_user is None:
            try:
                candidate_user = UserModel.objects.get(username__iexact=login_value)
            except UserModel.DoesNotExist:
                candidate_user = None

        if candidate_user is not None:
            # Force the canonical username into attrs so parent validation succeeds
            attrs["username"] = getattr(candidate_user, UserModel.USERNAME_FIELD)

        return super().validate(attrs)
