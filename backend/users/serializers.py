from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'email_verified')
        read_only_fields = ('email_verified',)
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Validate password strength
        try:
            validate_password(attrs['password'], self.instance)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Mark email as unverified by default
        user.email_verified = False
        user.save()
        return user
