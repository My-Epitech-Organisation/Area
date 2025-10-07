"""
Django management command to initialize the database with default services,
actions, and reactions.

This command populates the database with the core services needed for the AREA
application to function. It creates services like Timer, GitHub, Gmail, etc.,
along with their associated actions and reactions.

Usage:
    python manage.py init_services
    python manage.py init_services --reset  # Delete existing data first
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from automations.models import Action, Reaction, Service


class Command(BaseCommand):
    """Initialize database with default services, actions, and reactions."""

    help = "Initialize the database with default services, actions, and reactions"

    def add_arguments(self, parser):
        """Add custom command arguments."""
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing services, actions, and reactions before initializing",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        reset = options.get("reset", False)

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(
            self.style.SUCCESS("  AREA - Initializing Services Database")
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        if reset:
            self._reset_database()

        try:
            with transaction.atomic():
                self._create_services()
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 70))
            self.stdout.write(
                self.style.SUCCESS("✓ Database initialization completed successfully!")
            )
            self.stdout.write(self.style.SUCCESS("=" * 70))
            self._print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error during initialization: {e}"))
            raise CommandError(f"Failed to initialize database: {e}")

    def _reset_database(self):
        """Delete all existing services, actions, and reactions."""
        self.stdout.write(self.style.WARNING("→ Resetting database..."))

        action_count = Action.objects.count()
        reaction_count = Reaction.objects.count()
        service_count = Service.objects.count()

        Action.objects.all().delete()
        Reaction.objects.all().delete()
        Service.objects.all().delete()

        self.stdout.write(
            self.style.WARNING(
                f"  Deleted: {service_count} services, {action_count} actions, "
                f"{reaction_count} reactions"
            )
        )
        self.stdout.write("")

    def _create_services(self):
        """Create all services with their actions and reactions."""
        self.stdout.write(self.style.HTTP_INFO("→ Creating services...\n"))

        # Service definitions with their actions and reactions
        services_data = [
            {
                "name": "timer",
                "description": "Time-based triggers for scheduling automations",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "timer_daily",
                        "description": "Trigger at a specific time every day (e.g., 9:00 AM daily)",
                    },
                    {
                        "name": "timer_weekly",
                        "description": "Trigger at a specific time on specific days of the week (e.g., Monday 9:00 AM)",
                    },
                ],
                "reactions": [],
            },
            {
                "name": "github",
                "description": "GitHub repository management and notifications",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "github_new_issue",
                        "description": "Triggered when a new issue is created in a repository",
                    },
                    {
                        "name": "github_new_pr",
                        "description": "Triggered when a new pull request is opened",
                    },
                ],
                "reactions": [
                    {
                        "name": "github_create_issue",
                        "description": "Create a new issue in a GitHub repository",
                    },
                ],
            },
            {
                "name": "gmail",
                "description": "Gmail email integration for reading and sending emails",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "gmail_new_email",
                        "description": "Triggered when a new email is received matching specific criteria",
                    },
                ],
                "reactions": [],
            },
            {
                "name": "email",
                "description": "Generic email service for sending notifications",
                "status": Service.Status.ACTIVE,
                "actions": [],
                "reactions": [
                    {
                        "name": "send_email",
                        "description": "Send an email to specified recipients",
                    },
                ],
            },
            {
                "name": "slack",
                "description": "Slack messaging and notifications",
                "status": Service.Status.ACTIVE,
                "actions": [],
                "reactions": [
                    {
                        "name": "slack_message",
                        "description": "Send a message to a Slack channel or user",
                    },
                ],
            },
            {
                "name": "teams",
                "description": "Microsoft Teams messaging and collaboration",
                "status": Service.Status.ACTIVE,
                "actions": [],
                "reactions": [
                    {
                        "name": "teams_message",
                        "description": "Send a message to a Microsoft Teams channel",
                    },
                ],
            },
            {
                "name": "webhook",
                "description": "HTTP webhook integration for custom integrations",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "webhook_trigger",
                        "description": "Triggered when a webhook receives an HTTP request",
                    },
                ],
                "reactions": [
                    {
                        "name": "webhook_post",
                        "description": "Send an HTTP POST request to a specified URL",
                    },
                ],
            },
        ]

        # Create services
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data["name"],
                defaults={
                    "description": service_data["description"],
                    "status": service_data["status"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created service: {service.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Service already exists: {service.name} (skipped)"
                    )
                )

            # Create actions for this service
            for action_data in service_data["actions"]:
                action, created = Action.objects.get_or_create(
                    service=service,
                    name=action_data["name"],
                    defaults={"description": action_data["description"]},
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ Created action: {action.name} → {action.description}"
                        )
                    )

            # Create reactions for this service
            for reaction_data in service_data["reactions"]:
                reaction, created = Reaction.objects.get_or_create(
                    service=service,
                    name=reaction_data["name"],
                    defaults={"description": reaction_data["description"]},
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ Created reaction: {reaction.name} → {reaction.description}"
                        )
                    )

            self.stdout.write("")  # Empty line between services

    def _print_summary(self):
        """Print summary statistics."""
        service_count = Service.objects.count()
        action_count = Action.objects.count()
        reaction_count = Reaction.objects.count()

        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("📊 Summary:"))
        self.stdout.write(f"   • Services created: {service_count}")
        self.stdout.write(f"   • Actions created: {action_count}")
        self.stdout.write(f"   • Reactions created: {reaction_count}")
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO("🔗 Services are now available at:")
        )
        self.stdout.write("   • API: http://localhost:8080/api/services/")
        self.stdout.write("   • Admin: http://localhost:8080/admin/automations/service/")
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO("💡 Next steps:")
        )
        self.stdout.write("   1. Create a user account (signup)")
        self.stdout.write("   2. Connect OAuth2 services (Google, GitHub)")
        self.stdout.write("   3. Create your first AREA automation")
        self.stdout.write("")
