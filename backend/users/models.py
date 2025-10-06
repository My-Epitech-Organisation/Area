"""User models for the AREA project authentication system."""

import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        # username is optional, generate one if not provided
        if "username" not in extra_fields:
            extra_fields["username"] = ""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as login and username as display name.
    
    - Email is the unique identifier for authentication (USERNAME_FIELD)
    - Username is a simple display name (can have duplicates)
    - ID is a UUID for better security and scalability
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Override email to make it unique and required
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    
    # Override username to make it non-unique (just a display name)
    username = models.CharField(
        verbose_name="display name",
        max_length=150,
        blank=True,
        help_text="Optional display name (not unique, not used for login)",
    )
    
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, default="")

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = "email"
    # Fields required when creating a superuser (excluding USERNAME_FIELD and password)
    REQUIRED_FIELDS = []  # username is now optional
    
    # Use our custom manager
    objects = UserManager()

    def __str__(self):
        """Return string representation of the user."""
        return self.email


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
        return f"{self.user.email}'s token for {self.service_name}"


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
        return f"Reset token for {self.user.email}"

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
