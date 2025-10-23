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

        # 100 seconds - For Twitch action checking
        interval_100s, created = IntervalSchedule.objects.get_or_create(
            every=100, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 100-second interval"))

        # 60 seconds - For timer actions
        interval_60s, created = IntervalSchedule.objects.get_or_create(
            every=60, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 60-second interval"))

        # 300 seconds (5 minutes) - For GitHub actions
        interval_300s, created = IntervalSchedule.objects.get_or_create(
            every=300, period=IntervalSchedule.SECONDS
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✓ Created 300-second interval"))

        # =====================================================================
        # 2. Create periodic tasks
        # =====================================================================

        # Twitch actions check (every 100 seconds)
        task, created = PeriodicTask.objects.get_or_create(
            name="check-twitch-actions",
            defaults={
                "task": "automations.check_twitch_actions",
                "interval": interval_100s,
                "enabled": True,
                "start_time": timezone.now(),
                "description": "Check Twitch actions (stream status, followers, subscribers, etc.)",
            },
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "  ✓ Created check-twitch-actions task (100s interval)"
                )
            )
        else:
            # Update interval in case it changed
            if task.interval != interval_100s:
                task.interval = interval_100s
                task.save()
                self.stdout.write(
                    self.style.WARNING(
                        "  ⚠ Updated check-twitch-actions interval to 100s"
                    )
                )
            else:
                self.stdout.write("  • check-twitch-actions already exists")

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

        # GitHub actions check (every 300 seconds)
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

        # =====================================================================
        # Summary
        # =====================================================================
        total_tasks = PeriodicTask.objects.count()
        self.stdout.write(
            self.style.SUCCESS("\n✅ Celery Beat initialization complete!")
        )
        self.stdout.write(f"   Total periodic tasks: {total_tasks}")
        self.stdout.write(
            "\n💡 Note: For production, change Twitch interval to 300s (5 minutes)"
        )
