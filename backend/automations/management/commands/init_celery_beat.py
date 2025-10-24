"""
Management command to initialize Celery Beat periodic tasks.
This ensures all periodic tasks are created on every deployment.

Usage:
    python manage.py init_celery_beat
"""

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Initialize Celery Beat periodic tasks in the database"

    def handle(self, *args, **options):
        self.stdout.write("🔄 Initializing Celery Beat periodic tasks...")

        # =====================================================================
        # 1. Create interval schedules
        # =====================================================================

        # 60 seconds - For timer actions
        interval_60s, created = IntervalSchedule.objects.get_or_create(
            every=60, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 60-second interval"))

        # 120 seconds (2 minutes) - For real-time services (Twitch, Slack, Spotify)
        interval_120s, created = IntervalSchedule.objects.get_or_create(
            every=120, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 120-second interval"))

        # 300 seconds (5 minutes) - For email and repository services
        interval_300s, created = IntervalSchedule.objects.get_or_create(
            every=300, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 300-second interval"))

        # 1800 seconds (30 minutes) - For weather services
        interval_1800s, created = IntervalSchedule.objects.get_or_create(
            every=1800, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 1800-second interval"))

        # =====================================================================
        # 2. Create periodic tasks
        # =====================================================================

        # Timer actions check (every 60 seconds)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-timer-actions",
            defaults={
                "task": "automations.check_timer_actions",
                "interval": interval_60s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check timer-based actions (scheduled automations)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-timer-actions task (60s interval)"
                )
            )
        else:
            self.stdout.write("  • check-timer-actions already exists")

        # GitHub actions check (every 5 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-github-actions",
            defaults={
                "task": "automations.check_github_actions",
                "interval": interval_300s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check GitHub actions (repository events, issues, pull requests)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-github-actions task (300s interval)"
                )
            )
        else:
            self.stdout.write("  • check-github-actions already exists")

        # Gmail actions check (every 5 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-gmail-actions",
            defaults={
                "task": "automations.check_gmail_actions",
                "interval": interval_300s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check Gmail actions (new emails, labels, etc.)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-gmail-actions task (300s interval)"
                )
            )
        else:
            self.stdout.write("  • check-gmail-actions already exists")

        # Weather actions check (every 30 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-weather-actions",
            defaults={
                "task": "automations.check_weather_actions",
                "interval": interval_1800s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check weather conditions and trigger alerts",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-weather-actions task (1800s interval)"
                )
            )
        else:
            self.stdout.write("  • check-weather-actions already exists")

        # Twitch actions check (every 2 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-twitch-actions",
            defaults={
                "task": "automations.check_twitch_actions",
                "interval": interval_120s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check Twitch actions (stream status, followers, subscribers, etc.)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-twitch-actions task (120s interval)"
                )
            )
        else:
            self.stdout.write("  • check-twitch-actions already exists")

        # Slack actions check (every 2 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-slack-actions",
            defaults={
                "task": "automations.check_slack_actions",
                "interval": interval_120s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check Slack actions (new messages, keywords, mentions)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-slack-actions task (120s interval)"
                )
            )
        else:
            self.stdout.write("  • check-slack-actions already exists")

        # Spotify actions check (every 2 minutes)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-spotify-actions",
            defaults={
                "task": "automations.check_spotify_actions",
                "interval": interval_120s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check Spotify actions (playback, library changes)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-spotify-actions task (120s interval)"
                )
            )
        else:
            self.stdout.write("  • check-spotify-actions already exists")

        # =====================================================================
        # Summary
        # =====================================================================
        total_tasks = PeriodicTask.objects.count()
        self.stdout.write(
            self.style.SUCCESS("\n✅ Celery Beat initialization complete!")
        )
        self.stdout.write(f"   Total periodic tasks: {total_tasks}")
        self.stdout.write(
            "\n💡 Note: All polling tasks are now scheduled. Intervals can be adjusted per environment."
        )
