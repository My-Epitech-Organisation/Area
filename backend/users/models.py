"""User models for the AREA project authentication system."""

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with email verification support."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, default="")

    def __str__(self):
        """Return string representation of the user."""
        return self.username


class ServiceToken(models.Model):
    """Stores OAuth2 tokens for a user connected to an external service."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, default="")
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for ServiceToken model."""

        unique_together = ("user", "service_name")

    def __str__(self):
        """Return string representation of the service token."""
        return f"{self.user.username}'s token for {self.service_name}"
