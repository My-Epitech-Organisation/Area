"""
Django management command to sync Twitch EventSub subscription statuses.

This command queries the Twitch API to get the actual status of all EventSub
subscriptions and updates the local database accordingly.

Usage:
    python manage.py sync_twitch_subscriptions
"""

import logging

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from automations.models import TwitchEventSubSubscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync Twitch EventSub subscription statuses with Twitch API."""

    help = "Sync Twitch EventSub subscription statuses from Twitch API"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(
            self.style.SUCCESS("  Syncing Twitch EventSub Subscriptions")
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        # Get App Access Token
        try:
            app_token = self._get_app_access_token()
            client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to get Twitch credentials: {e}")
            )
            return

        # Get all subscriptions from Twitch API
        try:
            twitch_subscriptions = self._get_all_twitch_subscriptions(
                app_token, client_id
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Found {len(twitch_subscriptions)} subscriptions in Twitch API"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch subscriptions from Twitch: {e}")
            )
            return

        # Create lookup dict by subscription_id
        twitch_subs_dict = {sub["id"]: sub for sub in twitch_subscriptions}

        # Get all local subscriptions
        local_subscriptions = TwitchEventSubSubscription.objects.all()
        self.stdout.write(
            self.style.HTTP_INFO(
                f"→ Found {local_subscriptions.count()} subscriptions in local DB"
            )
        )
        self.stdout.write("")

        updated_count = 0
        error_count = 0

        for local_sub in local_subscriptions:
            try:
                twitch_sub = twitch_subs_dict.get(local_sub.subscription_id)

                if not twitch_sub:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Subscription {local_sub.subscription_id} not found in Twitch API"
                        )
                    )
                    # Mark as revoked if not found in Twitch
                    if local_sub.status != TwitchEventSubSubscription.Status.AUTHORIZATION_REVOKED:
                        local_sub.status = TwitchEventSubSubscription.Status.AUTHORIZATION_REVOKED
                        local_sub.save()
                        self.stdout.write(
                            self.style.WARNING(
                                f"    → Marked as REVOKED (user: {local_sub.user.username})"
                            )
                        )
                    continue

                # Get Twitch status
                twitch_status = twitch_sub["status"]

                # Map Twitch status to our status choices
                status_map = {
                    "enabled": TwitchEventSubSubscription.Status.ENABLED,
                    "webhook_callback_verification_pending": TwitchEventSubSubscription.Status.WEBHOOK_CALLBACK_VERIFICATION_PENDING,
                    "webhook_callback_verification_failed": TwitchEventSubSubscription.Status.WEBHOOK_CALLBACK_VERIFICATION_FAILED,
                    "notification_failures_exceeded": TwitchEventSubSubscription.Status.NOTIFICATION_FAILURES_EXCEEDED,
                    "authorization_revoked": TwitchEventSubSubscription.Status.AUTHORIZATION_REVOKED,
                    "moderator_removed": TwitchEventSubSubscription.Status.MODERATOR_REMOVED,
                    "user_removed": TwitchEventSubSubscription.Status.USER_REMOVED,
                    "version_removed": TwitchEventSubSubscription.Status.VERSION_REMOVED,
                }

                new_status = status_map.get(
                    twitch_status, 
                    TwitchEventSubSubscription.Status.ENABLED
                )

                # Update if different
                if local_sub.status != new_status:
                    old_status = local_sub.status
                    local_sub.status = new_status
                    local_sub.save()
                    updated_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Updated {local_sub.subscription_type} "
                            f"for {local_sub.user.username}: "
                            f"{old_status} → {new_status}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.HTTP_INFO(
                            f"  → {local_sub.subscription_type} "
                            f"for {local_sub.user.username}: "
                            f"{local_sub.status} (unchanged)"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error processing subscription {local_sub.pk}: {e}"
                    )
                )
                error_count += 1
                continue

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(
            self.style.SUCCESS(f"✓ Sync completed: {updated_count} updated")
        )
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f"  {error_count} errors encountered")
            )
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def _get_app_access_token(self) -> str:
        """Get Twitch App Access Token."""
        twitch_config = settings.OAUTH2_PROVIDERS["twitch"]
        client_id = twitch_config["client_id"]
        client_secret = twitch_config["client_secret"]

        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    def _get_all_twitch_subscriptions(
        self, app_token: str, client_id: str
    ) -> list:
        """Get all EventSub subscriptions from Twitch API."""
        all_subscriptions = []
        cursor = None

        while True:
            params = {}
            if cursor:
                params["after"] = cursor

            response = requests.get(
                "https://api.twitch.tv/helix/eventsub/subscriptions",
                headers={
                    "Authorization": f"Bearer {app_token}",
                    "Client-Id": client_id,
                },
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            all_subscriptions.extend(data.get("data", []))

            # Check for pagination
            pagination = data.get("pagination", {})
            cursor = pagination.get("cursor")

            if not cursor:
                break

        return all_subscriptions
