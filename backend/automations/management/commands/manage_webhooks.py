"""
Django management command to manage webhooks for GitHub, Twitch, and Slack.

Usage:
    python manage.py manage_webhooks --service github --action setup
    python manage.py manage_webhooks --service twitch --action list
    python manage.py manage_webhooks --service slack --action verify
"""

import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Manage external service webhooks."""

    help = "Manage webhooks for GitHub, Twitch, and Slack services"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--service",
            type=str,
            choices=["github", "twitch", "slack", "all"],
            required=True,
            help="Service to manage webhooks for",
        )
        parser.add_argument(
            "--action",
            type=str,
            choices=["setup", "verify", "list", "cleanup"],
            required=True,
            help="Action to perform",
        )
        parser.add_argument(
            "--webhook-url",
            type=str,
            help="Public webhook URL (e.g., https://your-domain.com)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        service = options["service"]
        action = options["action"]
        webhook_url = options.get("webhook_url")

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(
            self.style.SUCCESS(f"  Webhook Manager: {service.upper()} - {action.upper()}")
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        # Check webhook secrets configuration
        webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})

        if service == "all":
            services = ["github", "twitch", "slack"]
        else:
            services = [service]

        for svc in services:
            if svc not in webhook_secrets or not webhook_secrets[svc]:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {svc.upper()}: No webhook secret configured "
                        f"in settings.WEBHOOK_SECRETS['{svc}']"
                    )
                )
                self.stdout.write("")
                continue

            self.stdout.write(self.style.HTTP_INFO(f"→ Processing {svc.upper()}..."))
            self.stdout.write("")

            try:
                if action == "setup":
                    self._setup_webhook(svc, webhook_url)
                elif action == "verify":
                    self._verify_webhook(svc)
                elif action == "list":
                    self._list_webhooks(svc)
                elif action == "cleanup":
                    self._cleanup_webhooks(svc)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error processing {svc}: {e}")
                )
                if options.get("verbosity", 1) > 1:
                    logger.exception(f"Error in webhook management for {svc}")
            self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("✓ Webhook management complete"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def _setup_webhook(self, service: str, webhook_url: str | None = None):
        """Setup webhook configuration."""
        if not webhook_url:
            webhook_url = getattr(settings, "BACKEND_URL", "http://localhost:8080")

        full_webhook_url = f"{webhook_url}/webhooks/{service}/"

        self.stdout.write("  📝 Setup Instructions:")
        self.stdout.write("")

        if service == "github":
            self.stdout.write("  1. Go to your GitHub repository:")
            self.stdout.write("     https://github.com/<owner>/<repo>/settings/hooks")
            self.stdout.write("")
            self.stdout.write("  2. Click 'Add webhook'")
            self.stdout.write("")
            self.stdout.write(f"  3. Payload URL: {full_webhook_url}")
            self.stdout.write("")
            self.stdout.write("  4. Content type: application/json")
            self.stdout.write("")
            self.stdout.write("  5. Secret: (copy from settings.WEBHOOK_SECRETS['github'])")
            self.stdout.write("")
            self.stdout.write("  6. Select events:")
            self.stdout.write("     ☑ Issues")
            self.stdout.write("     ☑ Pull requests")
            self.stdout.write("     ☑ Pushes")
            self.stdout.write("")
            self.stdout.write("  7. Ensure webhook is Active")

        elif service == "twitch":
            self.stdout.write("  ⚠️  Twitch EventSub requires programmatic setup:")
            self.stdout.write("")
            self.stdout.write("  1. Get your Twitch Client ID and Secret")
            self.stdout.write("  2. Obtain an App Access Token:")
            self.stdout.write(
                "     POST https://id.twitch.tv/oauth2/token"
                "?client_id=<id>&client_secret=<secret>&grant_type=client_credentials"
            )
            self.stdout.write("")
            self.stdout.write("  3. Create EventSub subscriptions:")
            self.stdout.write(
                f"     POST https://api.twitch.tv/helix/eventsub/subscriptions"
            )
            self.stdout.write("     Body:")
            self.stdout.write("     {")
            self.stdout.write("       \"type\": \"stream.online\",")
            self.stdout.write("       \"version\": \"1\",")
            self.stdout.write(
                "       \"condition\": { \"broadcaster_user_id\": \"<user_id>\" },"
            )
            self.stdout.write("       \"transport\": {")
            self.stdout.write("         \"method\": \"webhook\",")
            self.stdout.write(f"         \"callback\": \"{full_webhook_url}\",")
            self.stdout.write("         \"secret\": \"<your_webhook_secret>\"")
            self.stdout.write("       }")
            self.stdout.write("     }")
            self.stdout.write("")
            self.stdout.write("  4. Repeat for other event types:")
            self.stdout.write("     - stream.offline")
            self.stdout.write("     - channel.follow")
            self.stdout.write("     - channel.subscribe")
            self.stdout.write("     - channel.update")
            self.stdout.write("")
            self.stdout.write(
                "  📚 Docs: https://dev.twitch.tv/docs/eventsub/manage-subscriptions"
            )

        elif service == "slack":
            self.stdout.write("  1. Go to your Slack App settings:")
            self.stdout.write("     https://api.slack.com/apps")
            self.stdout.write("")
            self.stdout.write("  2. Select your app (or create one)")
            self.stdout.write("")
            self.stdout.write("  3. Navigate to 'Event Subscriptions'")
            self.stdout.write("")
            self.stdout.write("  4. Enable Events: ON")
            self.stdout.write("")
            self.stdout.write(f"  5. Request URL: {full_webhook_url}")
            self.stdout.write("     (Slack will verify this URL)")
            self.stdout.write("")
            self.stdout.write("  6. Subscribe to bot events:")
            self.stdout.write("     ☑ message.channels")
            self.stdout.write("     ☑ app_mention")
            self.stdout.write("     ☑ member_joined_channel")
            self.stdout.write("")
            self.stdout.write("  7. Save Changes and Reinstall App")
            self.stdout.write("")
            self.stdout.write(
                "  📚 Docs: https://api.slack.com/events-api"
            )

    def _verify_webhook(self, service: str):
        """Verify webhook configuration."""
        webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})

        if service not in webhook_secrets:
            self.stdout.write(
                self.style.ERROR(f"  ✗ No webhook secret configured for {service}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Webhook secret configured for {service}")
        )

        # Check if Areas exist for this service
        from automations.models import Area, Service

        try:
            svc = Service.objects.get(name=service)
            active_areas = Area.objects.filter(
                action__service=svc, status=Area.Status.ACTIVE
            ).count()

            if active_areas > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {active_areas} active Area(s) using {service} actions"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  No active Areas using {service} actions"
                    )
                )
        except Service.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Service '{service}' not found in database")
            )

    def _list_webhooks(self, service: str):
        """List configured webhooks."""
        from automations.models import Area, Service

        try:
            svc = Service.objects.get(name=service)
            areas = Area.objects.filter(
                action__service=svc, status=Area.Status.ACTIVE
            ).select_related("action", "owner")

            if not areas.exists():
                self.stdout.write(f"  No active Areas for {service}")
                return

            self.stdout.write(
                f"  📋 Active Areas using {service} ({areas.count()}):"
            )
            self.stdout.write("")

            for area in areas:
                self.stdout.write(
                    f"    • {area.name} ({area.owner.username})"
                )
                self.stdout.write(
                    f"      Action: {area.action.name}"
                )
                if area.action_config:
                    self.stdout.write(
                        f"      Config: {area.action_config}"
                    )
                self.stdout.write("")

        except Service.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Service '{service}' not found")
            )

    def _cleanup_webhooks(self, service: str):
        """Cleanup webhook configuration."""
        self.stdout.write(
            self.style.WARNING(
                f"  ⚠️  Cleanup for {service} webhooks:"
            )
        )
        self.stdout.write("")
        self.stdout.write("  This would:")
        self.stdout.write(
            f"  • Remove {service} webhook subscriptions from external service"
        )
        self.stdout.write(
            f"  • Optionally disable polling for {service} actions"
        )
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING("  ⚠️  Manual cleanup required:")
        )

        if service == "github":
            self.stdout.write(
                "  - Remove webhook from GitHub repository settings"
            )
        elif service == "twitch":
            self.stdout.write(
                "  - Delete EventSub subscriptions via Twitch API"
            )
            self.stdout.write(
                "    DELETE https://api.twitch.tv/helix/eventsub/subscriptions?id=<subscription_id>"
            )
        elif service == "slack":
            self.stdout.write(
                "  - Disable Event Subscriptions in Slack App settings"
            )
