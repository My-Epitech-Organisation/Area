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
    """
    Stores OAuth2 tokens for external service connections.

    This model tracks OAuth2 access tokens, refresh tokens, and their
    expiration for services like Google, GitHub, etc. It supports automatic
    token refresh and expiration tracking.

    Attributes:
        user: The user who owns this token
        service_name: Name of the OAuth2 provider (google, github, etc.)
        access_token: Current OAuth2 access token
        refresh_token: OAuth2 refresh token (if supported by provider)
        expires_at: When the access token expires (None if never expires)
        scopes: Space-separated list of granted OAuth2 scopes
        token_type: Type of token (usually 'Bearer')
        created_at: When this token was first created
        updated_at: When this token was last updated (e.g., after refresh)
        last_used_at: When this token was last used for an API call
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_tokens",
        help_text="User who owns this OAuth2 token",
    )
    service_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="OAuth2 provider name (e.g., google, github)",
    )
    access_token = models.TextField(help_text="Current OAuth2 access token")
    refresh_token = models.TextField(
        blank=True,
        default="",
        help_text="OAuth2 refresh token (empty if not supported)",
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Token expiration time (None if never expires)",
    )

    # New fields for enhanced tracking
    scopes = models.TextField(
        blank=True,
        default="",
        help_text="Space-separated list of granted OAuth2 scopes",
    )
    token_type = models.CharField(
        max_length=20,
        default="Bearer",
        help_text="Token type (usually Bearer)",
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Last token update (e.g., after refresh)"
    )
    last_used_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time this token was used for an API call",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this token was first created"
    )

    class Meta:
        """Meta options for ServiceToken model."""

        unique_together = ("user", "service_name")
        ordering = ["-updated_at"]
        verbose_name = "Service Token"
        verbose_name_plural = "Service Tokens"
        indexes = [
            models.Index(fields=["user", "service_name"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["service_name"]),
        ]

    def __str__(self):
        """String representation of the service token."""
        status = "expired" if self.is_expired else "valid"
        return f"{self.user.email} - {self.service_name} ({status})"

    @property
    def is_expired(self) -> bool:
        """
        Check if the access token is expired.

        Returns:
            bool: True if token is expired, False otherwise
        """
        if not self.expires_at:
            return False
        return timezone.now() >= self.expires_at

    @property
    def needs_refresh(self) -> bool:
        """
        Check if the token should be refreshed soon.

        Tokens that expire in less than 5 minutes should be refreshed
        proactively to avoid expiration during use.

        Returns:
            bool: True if token expires in < 5 minutes, False otherwise
        """
        if not self.expires_at:
            return False
        threshold = timezone.now() + timedelta(minutes=5)
        return self.expires_at <= threshold

    @property
    def time_until_expiry(self) -> timedelta | None:
        """
        Calculate time remaining until token expires.

        Returns:
            timedelta: Time until expiration, or None if never expires
        """
        if not self.expires_at:
            return None
        return self.expires_at - timezone.now()

    def mark_used(self) -> None:
        """
        Mark this token as recently used.

        Updates last_used_at timestamp without triggering updated_at.
        """
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    def get_scopes_list(self) -> list[str]:
        """
        Get OAuth2 scopes as a list.

        Returns:
            list: List of scope strings
        """
        if not self.scopes:
            return []
        return [s.strip() for s in self.scopes.split() if s.strip()]

    def set_scopes_list(self, scopes: list[str]) -> None:
        """
        Set OAuth2 scopes from a list.

        Args:
            scopes: List of scope strings
        """
        self.scopes = " ".join(scopes) if scopes else ""


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


class OAuthNotification(models.Model):
    """
    Stores notifications about OAuth2 token issues.

    Alerts users when their OAuth2 tokens expire, fail to refresh,
    or encounter authentication issues requiring user intervention.

    Attributes:
        user: The user who needs to be notified
        service_name: Name of the affected service
        notification_type: Type of issue (token_expired, refresh_failed, etc.)
        message: Detailed message about the issue
        is_read: Whether the user has seen this notification
        is_resolved: Whether the issue has been fixed
        created_at: When the notification was created
        resolved_at: When the issue was resolved
    """

    class NotificationType(models.TextChoices):
        """Types of OAuth2 notifications."""

        TOKEN_EXPIRED = "token_expired", "Token Expired"
        REFRESH_FAILED = "refresh_failed", "Token Refresh Failed"
        AUTH_ERROR = "auth_error", "Authentication Error"
        REAUTH_REQUIRED = "reauth_required", "Reauthorization Required"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oauth_notifications",
        help_text="User who needs to be notified",
    )
    service_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the affected service (google, github, etc.)",
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.REAUTH_REQUIRED,
        help_text="Type of OAuth2 issue",
    )
    message = models.TextField(help_text="Detailed message about the issue")
    is_read = models.BooleanField(
        default=False, db_index=True, help_text="Has the user seen this notification"
    )
    is_resolved = models.BooleanField(
        default=False, db_index=True, help_text="Has the issue been fixed"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the notification was created"
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the issue was resolved (e.g., user reconnected)",
    )

    class Meta:
        """Meta options for OAuthNotification model."""

        ordering = ["-created_at"]
        verbose_name = "OAuth Notification"
        verbose_name_plural = "OAuth Notifications"
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "is_resolved"]),
            models.Index(fields=["service_name", "is_resolved"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        """String representation of the notification."""
        status = "read" if self.is_read else "unread"
        return (
            f"{self.user.email} - {self.service_name} "
            f"{self.get_notification_type_display()} ({status})"
        )

    def mark_read(self) -> None:
        """Mark this notification as read by the user."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])

    def resolve(self) -> None:
        """
        Mark this notification as resolved.

        Should be called when the user reconnects the service
        or the token refresh succeeds.
        """
        if not self.is_resolved:
            self.is_resolved = True
            self.resolved_at = timezone.now()
            self.save(update_fields=["is_resolved", "resolved_at"])

    @classmethod
    def create_notification(
        cls,
        user,
        service_name: str,
        notification_type: str,
        message: str,
    ) -> "OAuthNotification":
        """
        Create a new OAuth notification.

        Avoids creating duplicate unresolved notifications for the
        same user and service.

        Args:
            user: Django User instance
            service_name: Name of the service
            notification_type: Type of notification (from NotificationType)
            message: Detailed message

        Returns:
            OAuthNotification: Created or existing notification
        """
        # Check for existing unresolved notification
        existing = cls.objects.filter(
            user=user,
            service_name=service_name,
            notification_type=notification_type,
            is_resolved=False,
        ).first()

        if existing:
            # Update message if it changed
            if existing.message != message:
                existing.message = message
                existing.save(update_fields=["message"])
            return existing

        # Create new notification
        return cls.objects.create(
            user=user,
            service_name=service_name,
            notification_type=notification_type,
            message=message,
        )

    @classmethod
    def resolve_for_service(cls, user, service_name: str) -> int:
        """
        Resolve all notifications for a user and service.

        Should be called when the user successfully reconnects a service.

        Args:
            user: Django User instance
            service_name: Name of the service

        Returns:
            int: Number of notifications resolved
        """
        now = timezone.now()
        return cls.objects.filter(
            user=user, service_name=service_name, is_resolved=False
        ).update(is_resolved=True, resolved_at=now)
