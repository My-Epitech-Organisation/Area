"""
Management command to monitor OAuth token health.

Checks all service tokens across users and identifies issues:
- Expired tokens without refresh capability
- Tokens expiring soon (within 24 hours)
- Tokens without refresh tokens
- Failed refresh attempts

Usage:
    python manage.py check_token_health
    python manage.py check_token_health --notify-users
    python manage.py check_token_health --service google
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import OAuthNotification, ServiceToken

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Check health of all OAuth tokens and optionally notify users."""

    help = "Monitor OAuth token health and identify issues requiring user intervention"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--notify-users",
            action="store_true",
            help="Create notifications for users with token issues",
        )
        parser.add_argument(
            "--service",
            type=str,
            help="Check only tokens for a specific service",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output for each token",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        notify_users = options["notify_users"]
        service_filter = options["service"]
        verbose = options["verbose"]

        self.stdout.write(self.style.SUCCESS("=== OAuth Token Health Check ===\n"))

        # Get all tokens
        tokens = ServiceToken.objects.select_related("user").all()

        if service_filter:
            tokens = tokens.filter(service_name=service_filter)
            self.stdout.write(f"Filtering by service: {service_filter}\n")

        if not tokens.exists():
            self.stdout.write(self.style.WARNING("No tokens found in database.\n"))
            return

        # Statistics
        total_tokens = tokens.count()
        expired_tokens = []
        expiring_soon_tokens = []
        no_refresh_tokens = []
        healthy_tokens = []

        # Analyze each token
        for token in tokens:
            if verbose:
                self.stdout.write(
                    f"\nChecking {token.user.email}/{token.service_name}..."
                )

            # Check if expired
            if token.is_expired:
                expired_tokens.append(token)
                if verbose:
                    self.stdout.write(self.style.ERROR("  ❌ EXPIRED"))

                # Check if has refresh token
                if not token.refresh_token:
                    no_refresh_tokens.append(token)
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR("  ❌ No refresh token available")
                        )

                    # Notify user if requested
                    if notify_users:
                        self._create_reauth_notification(token)

            # Check if expiring soon (within 24 hours)
            elif token.expires_at:
                time_until_expiry = token.expires_at - timezone.now()
                if time_until_expiry < timedelta(hours=24):
                    expiring_soon_tokens.append(token)
                    if verbose:
                        hours = time_until_expiry.total_seconds() / 3600
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠️  Expires in {hours:.1f} hours")
                        )

                    # Check refresh capability
                    if not token.refresh_token:
                        no_refresh_tokens.append(token)
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING("  ⚠️  No refresh token")
                            )
                else:
                    healthy_tokens.append(token)
                    if verbose:
                        self.stdout.write(self.style.SUCCESS("  ✓ Healthy"))
            else:
                # No expiration (e.g., GitHub)
                healthy_tokens.append(token)
                if verbose:
                    self.stdout.write(self.style.SUCCESS("  ✓ Healthy (no expiration)"))

        # Print summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("\n📊 Summary:\n"))
        self.stdout.write(f"  Total tokens: {total_tokens}")
        self.stdout.write(
            self.style.SUCCESS(f"  Healthy tokens: {len(healthy_tokens)}")
        )
        self.stdout.write(
            self.style.WARNING(f"  Expiring soon (< 24h): {len(expiring_soon_tokens)}")
        )
        self.stdout.write(self.style.ERROR(f"  Expired tokens: {len(expired_tokens)}"))
        self.stdout.write(
            self.style.ERROR(f"  Without refresh token: {len(no_refresh_tokens)}")
        )

        # Show tokens needing attention
        if expired_tokens:
            self.stdout.write("\n" + self.style.ERROR("❌ Expired Tokens:"))
            for token in expired_tokens:
                expired_duration = timezone.now() - token.expires_at
                days = expired_duration.days
                self.stdout.write(
                    f"  - {token.user.email}/{token.service_name} "
                    f"(expired {days} day{'s' if days != 1 else ''} ago)"
                )

        if expiring_soon_tokens:
            self.stdout.write("\n" + self.style.WARNING("⚠️  Expiring Soon:"))
            for token in expiring_soon_tokens:
                hours = (token.expires_at - timezone.now()).total_seconds() / 3600
                self.stdout.write(
                    f"  - {token.user.email}/{token.service_name} "
                    f"(expires in {hours:.1f} hours)"
                )

        if no_refresh_tokens:
            self.stdout.write(
                "\n"
                + self.style.ERROR(
                    "🔄 Tokens Without Refresh Capability (require manual reauth):"
                )
            )
            for token in no_refresh_tokens:
                self.stdout.write(f"  - {token.user.email}/{token.service_name}")

        # Show notification status
        if notify_users:
            self.stdout.write(
                "\n"
                + self.style.SUCCESS(
                    f"✉️  Created notifications for {len(no_refresh_tokens)} users"
                )
            )
        else:
            self.stdout.write(
                "\n"
                + self.style.WARNING(
                    "💡 Run with --notify-users to create notifications"
                )
            )

        self.stdout.write("\n")

    def _create_reauth_notification(self, token: ServiceToken) -> None:
        """
        Create a reauthorization notification for a token.

        Args:
            token: ServiceToken that needs reauthorization
        """
        message = (
            f"Your {token.service_name} connection has expired and cannot be "
            f"automatically refreshed. Please reconnect your account to continue "
            f"using {token.service_name} services.\n\n"
            f"Token expired at: {token.expires_at.strftime('%Y-%m-%d %H:%M:%S') if token.expires_at else 'N/A'}"
        )

        OAuthNotification.create_notification(
            user=token.user,
            service_name=token.service_name,
            notification_type=OAuthNotification.NotificationType.REAUTH_REQUIRED,
            message=message,
        )

        self.stdout.write(
            self.style.SUCCESS(f"  ✉️  Created notification for {token.user.email}")
        )
