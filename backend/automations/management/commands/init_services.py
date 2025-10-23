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


def convert_to_json_schema(config_schema):
    """
    Convert our custom config schema to JSON Schema format.

    Our format:
    {
        "field_name": {
            "type": "string",
            "label": "...",
            "required": true,
            ...
        }
    }

    JSON Schema format:
    {
        "properties": {
            "field_name": {
                "type": "string",
                ...
            }
        },
        "required": ["field_name"]
    }
    """
    if not config_schema:
        return {}

    properties = {}
    required = []

    for field_name, field_config in config_schema.items():
        # Extract required flag
        is_required = field_config.get("required", False)
        if is_required:
            required.append(field_name)

        # Build property config (remove custom fields)
        prop = {k: v for k, v in field_config.items() if k != "required"}
        properties[field_name] = prop

    result = {"properties": properties}
    if required:
        result["required"] = required

    return result


class Command(BaseCommand):
    """Initialize database with default services, actions, and reactions."""

    help = "Initialize the database with default services, actions, and reactions"

    def add_arguments(self, parser):
        """Add custom command arguments."""
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Delete all existing services, actions, and reactions "
                "before initializing"
            ),
        )

    def handle(self, *args, **options):
        """Execute the command."""
        reset = options.get("reset", False)

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  AREA - Initializing Services Database"))
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
            raise CommandError(f"Failed to initialize database: {e}") from e

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
                        "description": (
                            "Trigger at a specific time every day "
                            "(e.g., 9:00 AM daily)"
                        ),
                    },
                    {
                        "name": "timer_weekly",
                        "description": (
                            "Trigger at a specific time on specific days "
                            "of the week (e.g., Monday 9:00 AM)"
                        ),
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
                        "description": (
                            "Triggered when a new issue is created in a repository"
                        ),
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
                        "description": "Triggered when any new unread email is received",
                        "config_schema": {},
                    },
                    {
                        "name": "gmail_new_from_sender",
                        "description": (
                            "Triggered when email from specific sender is received"
                        ),
                        "config_schema": {
                            "sender_email": {
                                "type": "string",
                                "label": "Sender Email",
                                "description": "Email address to monitor (e.g., boss@company.com)",
                                "required": True,
                                "placeholder": "example@gmail.com",
                            },
                        },
                    },
                    {
                        "name": "gmail_new_with_label",
                        "description": (
                            "Triggered when email with specific label is received"
                        ),
                        "config_schema": {
                            "label_name": {
                                "type": "string",
                                "label": "Gmail Label",
                                "description": "Name of the Gmail label to monitor",
                                "required": True,
                                "placeholder": "Important",
                            },
                        },
                    },
                    {
                        "name": "gmail_new_with_subject",
                        "description": (
                            "Triggered when email with subject containing text is received"
                        ),
                        "config_schema": {
                            "subject_text": {
                                "type": "string",
                                "label": "Subject Contains",
                                "description": "Text that must appear in the email subject",
                                "required": True,
                                "placeholder": "URGENT",
                            },
                        },
                    },
                ],
                "reactions": [
                    {
                        "name": "gmail_send_email",
                        "description": "Send an email via Gmail",
                        "config_schema": {
                            "to": {
                                "type": "string",
                                "label": "Recipient Email",
                                "description": "Email address of the recipient",
                                "required": True,
                                "placeholder": "example@gmail.com",
                            },
                            "subject": {
                                "type": "string",
                                "label": "Subject",
                                "description": "Email subject line",
                                "required": True,
                                "placeholder": "Important notification",
                            },
                            "body": {
                                "type": "text",
                                "label": "Email Body",
                                "description": "Email message content (supports variables: {trigger_data})",
                                "required": True,
                                "placeholder": "This is an automated message...",
                            },
                        },
                    },
                    {
                        "name": "gmail_mark_read",
                        "description": "Mark an email as read",
                        "config_schema": {
                            "message_id": {
                                "type": "string",
                                "label": "Message ID",
                                "description": "Gmail message ID (automatically provided by trigger)",
                                "required": False,
                                "default": "{message_id}",
                            },
                        },
                    },
                    {
                        "name": "gmail_add_label",
                        "description": "Add a label to an email",
                        "config_schema": {
                            "message_id": {
                                "type": "string",
                                "label": "Message ID",
                                "description": "Gmail message ID (automatically provided by trigger)",
                                "required": False,
                                "default": "{message_id}",
                            },
                            "label_name": {
                                "type": "string",
                                "label": "Label Name",
                                "description": "Name of the label to add",
                                "required": True,
                                "placeholder": "Important",
                            },
                        },
                    },
                ],
            },
            {
                "name": "google_calendar",
                "description": "Google Calendar integration for events and scheduling",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "calendar_event_starting_soon",
                        "description": ("Triggered when event starts in X minutes"),
                        "config_schema": {
                            "minutes_before": {
                                "type": "number",
                                "label": "Minutes Before",
                                "description": "Trigger this many minutes before event starts",
                                "required": True,
                                "default": 15,
                                "min": 1,
                                "max": 1440,
                            },
                        },
                    },
                    {
                        "name": "calendar_new_event",
                        "description": "Triggered when new event is created",
                        "config_schema": {},
                    },
                ],
                "reactions": [
                    {
                        "name": "calendar_create_event",
                        "description": "Create a new calendar event",
                        "config_schema": {
                            "summary": {
                                "type": "string",
                                "label": "Event Title",
                                "description": "Title of the calendar event",
                                "required": True,
                                "placeholder": "Team meeting",
                            },
                            "description": {
                                "type": "text",
                                "label": "Event Description",
                                "description": "Detailed description of the event",
                                "required": False,
                                "placeholder": "Discuss project updates...",
                            },
                            "start_time": {
                                "type": "datetime",
                                "label": "Start Time",
                                "description": "Event start date and time (ISO 8601 format or relative like '+1 hour')",
                                "required": True,
                                "placeholder": "2025-10-15T14:00:00",
                            },
                            "end_time": {
                                "type": "datetime",
                                "label": "End Time",
                                "description": "Event end date and time (ISO 8601 format or relative like '+2 hours')",
                                "required": True,
                                "placeholder": "2025-10-15T15:00:00",
                            },
                            "attendees": {
                                "type": "string",
                                "label": "Attendees",
                                "description": "Comma-separated email addresses of attendees",
                                "required": False,
                                "placeholder": "john@example.com, jane@example.com",
                            },
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Event location (physical or virtual)",
                                "required": False,
                                "placeholder": "Conference Room A",
                            },
                        },
                    },
                    {
                        "name": "calendar_update_event",
                        "description": "Update an existing calendar event",
                        "config_schema": {
                            "event_id": {
                                "type": "string",
                                "label": "Event ID",
                                "description": "Calendar event ID (automatically provided by trigger)",
                                "required": False,
                                "default": "{event_id}",
                            },
                            "summary": {
                                "type": "string",
                                "label": "New Event Title",
                                "description": "Updated title for the event",
                                "required": False,
                                "placeholder": "Team meeting (Rescheduled)",
                            },
                            "description": {
                                "type": "text",
                                "label": "New Description",
                                "description": "Updated event description",
                                "required": False,
                                "placeholder": "Updated agenda...",
                            },
                            "start_time": {
                                "type": "datetime",
                                "label": "New Start Time",
                                "description": "Updated start date and time",
                                "required": False,
                                "placeholder": "2025-10-15T15:00:00",
                            },
                            "end_time": {
                                "type": "datetime",
                                "label": "New End Time",
                                "description": "Updated end date and time",
                                "required": False,
                                "placeholder": "2025-10-15T16:00:00",
                            },
                        },
                    },
                ],
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
                        "description": (
                            "Triggered when a webhook receives an HTTP request"
                        ),
                    },
                ],
                "reactions": [
                    {
                        "name": "webhook_post",
                        "description": "Send an HTTP POST request to a specified URL",
                    },
                ],
            },
            {
                "name": "twitch",
                "description": "Twitch streaming platform integration for channels and chat",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "twitch_stream_online",
                        "description": "Triggered when a channel goes live",
                        "config_schema": {
                            "broadcaster_login": {
                                "type": "string",
                                "label": "Broadcaster Username",
                                "description": "Twitch username of the broadcaster to monitor",
                                "required": True,
                                "placeholder": "shroud",
                            },
                        },
                    },
                    {
                        "name": "twitch_stream_offline",
                        "description": "Triggered when a channel goes offline",
                        "config_schema": {
                            "broadcaster_login": {
                                "type": "string",
                                "label": "Broadcaster Username",
                                "description": "Twitch username of the broadcaster to monitor",
                                "required": True,
                                "placeholder": "shroud",
                            },
                        },
                    },
                    {
                        "name": "twitch_new_follower",
                        "description": "Triggered when someone follows the channel",
                        "config_schema": {},
                    },
                    {
                        "name": "twitch_new_subscriber",
                        "description": "Triggered when someone subscribes to the channel",
                        "config_schema": {},
                    },
                    {
                        "name": "twitch_channel_update",
                        "description": "Triggered when channel info changes (title, category, etc.)",
                        "config_schema": {},
                    },
                ],
                "reactions": [
                    {
                        "name": "twitch_send_chat_message",
                        "description": "Send a message in your Twitch chat",
                        "config_schema": {
                            "message": {
                                "type": "text",
                                "label": "Message",
                                "description": "Message to send in your chat",
                                "required": True,
                                "placeholder": "Thanks for the follow!",
                            },
                        },
                    },
                    {
                        "name": "twitch_send_whisper",
                        "description": "Send a private message (whisper) to a Twitch user",
                        "config_schema": {
                            "to_user": {
                                "type": "string",
                                "label": "Recipient Username",
                                "description": "Twitch username to send the whisper to",
                                "required": True,
                                "placeholder": "username",
                            },
                            "message": {
                                "type": "text",
                                "label": "Message",
                                "description": "Private message to send",
                                "required": True,
                                "placeholder": "Thanks for the follow!",
                            },
                        },
                    },
                    {
                        "name": "twitch_send_announcement",
                        "description": "Send an announcement in your Twitch chat",
                        "config_schema": {
                            "message": {
                                "type": "text",
                                "label": "Announcement Message",
                                "description": "Announcement message to display",
                                "required": True,
                                "placeholder": "Stream starting soon!",
                            },
                            "color": {
                                "type": "string",
                                "label": "Color",
                                "description": "Announcement color (primary, blue, green, orange, purple)",
                                "required": False,
                                "default": "primary",
                            },
                        },
                    },
                    {
                        "name": "twitch_create_clip",
                        "description": "Create a clip from your live stream",
                        "config_schema": {},
                    },
                    {
                        "name": "twitch_update_title",
                        "description": "Update your stream title",
                        "config_schema": {
                            "title": {
                                "type": "string",
                                "label": "Stream Title",
                                "description": "New stream title (supports variables)",
                                "required": True,
                                "placeholder": "Playing {game_name}!",
                            },
                        },
                    },
                    {
                        "name": "twitch_update_category",
                        "description": "Update your stream category/game",
                        "config_schema": {
                            "game_name": {
                                "type": "string",
                                "label": "Game/Category Name",
                                "description": "Name of the game or category",
                                "required": True,
                                "placeholder": "Just Chatting",
                            },
                        },
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
                # Convert custom schema to JSON Schema format
                raw_schema = action_data.get("config_schema", {})
                json_schema = convert_to_json_schema(raw_schema)

                action, created = Action.objects.get_or_create(
                    service=service,
                    name=action_data["name"],
                    defaults={
                        "description": action_data["description"],
                        "config_schema": json_schema,
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ Created action: {action.name} → "
                            f"{action.description}"
                        )
                    )
                else:
                    # Update config_schema if it changed
                    if raw_schema:
                        action.config_schema = json_schema
                        action.save()

            # Create reactions for this service
            for reaction_data in service_data["reactions"]:
                # Convert custom schema to JSON Schema format
                raw_schema = reaction_data.get("config_schema", {})
                json_schema = convert_to_json_schema(raw_schema)

                reaction, created = Reaction.objects.get_or_create(
                    service=service,
                    name=reaction_data["name"],
                    defaults={
                        "description": reaction_data["description"],
                        "config_schema": json_schema,
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ Created reaction: {reaction.name} → "
                            f"{reaction.description}"
                        )
                    )
                else:
                    # Update config_schema if it changed
                    if raw_schema:
                        reaction.config_schema = json_schema
                        reaction.save()

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
        self.stdout.write(self.style.HTTP_INFO("🔗 Services are now available at:"))
        self.stdout.write("   • API: http://localhost:8080/api/services/")
        self.stdout.write(
            "   • Admin: http://localhost:8080/admin/automations/service/"
        )
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("💡 Next steps:"))
        self.stdout.write("   1. Create a user account (signup)")
        self.stdout.write("   2. Connect OAuth2 services (Google, GitHub)")
        self.stdout.write("   3. Create your first AREA automation")
        self.stdout.write("")
