"""User models for the AREA project authentication system."""

import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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


class PasswordResetToken(models.Model):
    """Stores password reset tokens with expiration."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        """Meta options for PasswordResetToken model."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return string representation of the password reset token."""
        return f"Reset token for {self.user.username}"

    def save(self, *args, **kwargs):
        """Override save to generate token and set expiration."""
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            # Token expires in 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        """Check if token is still valid (not expired and not used)."""
        return not self.used and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark token as used."""
        self.used = True
        self.save()
