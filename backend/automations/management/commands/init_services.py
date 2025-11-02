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

    # Valid JSON Schema keywords to keep
    valid_json_schema_keys = {
        "type",
        "enum",
        "format",
        "pattern",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "default",
        "description",
        "items",
        "properties",
        "additionalProperties",
        "minItems",
        "maxItems",
    }

    for field_name, field_config in config_schema.items():
        # Extract required flag
        is_required = field_config.get("required", False)
        if is_required:
            required.append(field_name)

        # Build property config (keep only valid JSON Schema fields)
        prop = {k: v for k, v in field_config.items() if k in valid_json_schema_keys}
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
                                "minimum": 1,
                                "maximum": 1440,
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
                        "config_schema": {
                            "recipient": {
                                "type": "string",
                                "label": "Recipient Email",
                                "description": "Email address of the recipient",
                                "required": True,
                                "placeholder": "user@example.com",
                            },
                            "subject": {
                                "type": "string",
                                "label": "Email Subject",
                                "description": "Subject line of the email",
                                "required": True,
                                "placeholder": "AREA Notification",
                            },
                            "body": {
                                "type": "text",
                                "label": "Email Body",
                                "description": "Content of the email message",
                                "required": True,
                                "placeholder": "This is an automated notification from your AREA automation.",
                            },
                        },
                    },
                ],
            },
            {
                "name": "slack",
                "description": "Slack messaging and team collaboration platform",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "slack_new_message",
                        "description": "Triggered when a new message is posted in a channel",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to monitor (e.g., #general or C1234567890)",
                                "required": True,
                                "placeholder": "#general",
                            },
                        },
                    },
                    {
                        "name": "slack_message_with_keyword",
                        "description": "Triggered when a message contains specific keywords",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to monitor (leave empty for all channels)",
                                "required": False,
                                "placeholder": "#general",
                            },
                            "keywords": {
                                "type": "string",
                                "label": "Keywords",
                                "description": "Comma-separated keywords to trigger on",
                                "required": True,
                                "placeholder": "urgent,important,help",
                            },
                        },
                    },
                    {
                        "name": "slack_user_mention",
                        "description": "Triggered when you are mentioned in a message",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to monitor (leave empty for all channels)",
                                "required": False,
                                "placeholder": "#general",
                            },
                        },
                    },
                    {
                        "name": "slack_channel_join",
                        "description": "Triggered when a user joins a channel",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to monitor",
                                "required": True,
                                "placeholder": "#general",
                            },
                        },
                    },
                ],
                "reactions": [
                    {
                        "name": "slack_send_message",
                        "description": "Send a message to a Slack channel",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to send to (with or without #)",
                                "required": True,
                                "placeholder": "#general",
                            },
                            "message": {
                                "type": "text",
                                "label": "Message",
                                "description": "Message to send (supports variables: {trigger_data})",
                                "required": True,
                                "placeholder": "Hello from AREA!",
                            },
                            "username": {
                                "type": "string",
                                "label": "Bot Username",
                                "description": "Display name for the bot (optional)",
                                "required": False,
                                "placeholder": "AREA Bot",
                            },
                            "icon_emoji": {
                                "type": "string",
                                "label": "Bot Icon",
                                "description": "Emoji icon for the bot (optional, e.g., :robot_face:)",
                                "required": False,
                                "placeholder": ":robot_face:",
                            },
                        },
                    },
                    {
                        "name": "slack_send_thread_reply",
                        "description": "Reply to a message in a thread",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel containing the thread",
                                "required": True,
                                "placeholder": "#general",
                            },
                            "thread_ts": {
                                "type": "string",
                                "label": "Thread Timestamp",
                                "description": "Thread timestamp to reply to (from trigger data)",
                                "required": False,
                                "default": "{thread_ts}",
                                "placeholder": "{thread_ts}",
                            },
                            "message": {
                                "type": "text",
                                "label": "Reply Message",
                                "description": "Reply message content",
                                "required": True,
                                "placeholder": "Thanks for the update!",
                            },
                        },
                    },
                    {
                        "name": "slack_send_alert",
                        "description": "Send an alert message to a channel",
                        "config_schema": {
                            "channel": {
                                "type": "string",
                                "label": "Channel",
                                "description": "Slack channel to send alert to",
                                "required": True,
                                "placeholder": "#alerts",
                            },
                            "alert_type": {
                                "type": "string",
                                "label": "Alert Type",
                                "description": "Type of alert (info, warning, error)",
                                "required": False,
                                "default": "info",
                                "enum": ["info", "warning", "error"],
                            },
                            "title": {
                                "type": "string",
                                "label": "Alert Title",
                                "description": "Alert title/message",
                                "required": True,
                                "placeholder": "System Alert",
                            },
                            "details": {
                                "type": "text",
                                "label": "Alert Details",
                                "description": "Additional alert details (optional)",
                                "required": False,
                                "placeholder": "Additional context...",
                            },
                        },
                    },
                ],
            },
            {
                "name": "weather",
                "description": "Weather data and alerts integration",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "weather_rain_detected",
                        "description": "Triggered when rain is detected in the specified location",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "Paris, France",
                            },
                        },
                    },
                    {
                        "name": "weather_snow_detected",
                        "description": "Triggered when snow is detected in the specified location",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "New York, NY",
                            },
                        },
                    },
                    {
                        "name": "weather_temperature_above",
                        "description": "Triggered when temperature rises above the specified threshold",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "London, UK",
                            },
                            "threshold": {
                                "type": "number",
                                "label": "Temperature Threshold (°C)",
                                "description": "Trigger when temperature exceeds this value",
                                "required": True,
                                "default": 25,
                                "minimum": -50,
                                "maximum": 60,
                            },
                        },
                    },
                    {
                        "name": "weather_temperature_below",
                        "description": "Triggered when temperature drops below the specified threshold",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "Moscow, Russia",
                            },
                            "threshold": {
                                "type": "number",
                                "label": "Temperature Threshold (°C)",
                                "description": "Trigger when temperature falls below this value",
                                "required": True,
                                "default": 0,
                                "minimum": -50,
                                "maximum": 60,
                            },
                        },
                    },
                    {
                        "name": "weather_extreme_heat",
                        "description": "Triggered when extreme heat is detected (>35°C)",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "Phoenix, AZ",
                            },
                        },
                    },
                    {
                        "name": "weather_extreme_cold",
                        "description": "Triggered when extreme cold is detected (<-10°C)",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "Anchorage, AK",
                            },
                        },
                    },
                    {
                        "name": "weather_windy",
                        "description": "Triggered when strong winds are detected",
                        "config_schema": {
                            "location": {
                                "type": "string",
                                "label": "Location",
                                "description": "Location to monitor (city name or coordinates)",
                                "required": True,
                                "placeholder": "Chicago, IL",
                            },
                            "threshold": {
                                "type": "number",
                                "label": "Wind Speed Threshold (km/h)",
                                "description": "Trigger when wind speed exceeds this value (km/h)",
                                "required": True,
                                "default": 50,
                                "minimum": 0,
                                "maximum": 300,
                            },
                        },
                    },
                ],
                "reactions": [],
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
            {
                "name": "debug",
                "description": "Internal debugging service for manual testing and development",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "debug_manual_trigger",
                        "description": "Manually triggered action for testing (no automatic polling)",
                        "config_schema": {},
                    },
                ],
                "reactions": [
                    {
                        "name": "debug_log_execution",
                        "description": "Log execution details with timestamp for debugging",
                        "config_schema": {
                            "message": {
                                "type": "string",
                                "label": "Custom Message",
                                "description": "Optional custom message to log",
                                "required": False,
                                "placeholder": "Debug execution triggered",
                            },
                        },
                    },
                ],
            },
            {
                "name": "spotify",
                "description": "Spotify integration for music playback and library management",
                "status": Service.Status.ACTIVE,
                "actions": [],
                "reactions": [
                    {
                        "name": "spotify_play_track",
                        "description": "Play a specific track on Spotify",
                        "config_schema": {
                            "track_uri": {
                                "type": "string",
                                "label": "Track URI",
                                "description": "Spotify URI of the track to play (spotify:track:...)",
                                "required": True,
                                "placeholder": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                            },
                            "position_ms": {
                                "type": "number",
                                "label": "Start Position (ms)",
                                "description": "Position to start playing from in milliseconds",
                                "required": False,
                                "default": 0,
                                "minimum": 0,
                            },
                        },
                    },
                    {
                        "name": "spotify_pause_playback",
                        "description": "Pause the currently playing track",
                        "config_schema": {},
                    },
                    {
                        "name": "spotify_resume_playback",
                        "description": "Resume playback of the current track",
                        "config_schema": {},
                    },
                    {
                        "name": "spotify_skip_next",
                        "description": "Skip to the next track in the queue",
                        "config_schema": {},
                    },
                    {
                        "name": "spotify_skip_previous",
                        "description": "Skip to the previous track",
                        "config_schema": {},
                    },
                    {
                        "name": "spotify_set_volume",
                        "description": "Set the playback volume",
                        "config_schema": {
                            "volume_percent": {
                                "type": "number",
                                "label": "Volume (%)",
                                "description": "Volume level as percentage (0-100)",
                                "required": True,
                                "minimum": 0,
                                "maximum": 100,
                                "default": 50,
                            },
                        },
                    },
                    {
                        "name": "spotify_create_playlist",
                        "description": "Create a new playlist",
                        "config_schema": {
                            "name": {
                                "type": "string",
                                "label": "Playlist Name",
                                "description": "Name for the new playlist",
                                "required": True,
                                "placeholder": "My New Playlist",
                            },
                            "description": {
                                "type": "string",
                                "label": "Description",
                                "description": "Optional description for the playlist",
                                "required": False,
                                "placeholder": "A playlist created by AREA",
                            },
                            "public": {
                                "type": "boolean",
                                "label": "Public",
                                "description": "Make the playlist public",
                                "required": False,
                                "default": False,
                            },
                        },
                    },
                ],
            },
            {
                "name": "notion",
                "description": "Notion workspace and document management integration",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "notion_page_created",
                        "description": "Triggered when a new page is created in a workspace",
                        "config_schema": {},
                    },
                    {
                        "name": "notion_page_updated",
                        "description": "Triggered when a page is updated in a workspace",
                        "config_schema": {},
                    },
                    {
                        "name": "notion_database_item_added",
                        "description": "Triggered when a new item is added to a database",
                        "config_schema": {
                            "database_id": {
                                "type": "string",
                                "label": "Database Name or ID",
                                "description": "Database name (e.g., 'AREA Tasks'), ID (UUID), or full Notion database URL",
                                "required": True,
                                "placeholder": "AREA Tasks or 12345678-1234-1234-1234-123456789012",
                            },
                        },
                    },
                ],
                "reactions": [
                    {
                        "name": "notion_create_page",
                        "description": "Create a new page in a Notion workspace",
                        "config_schema": {
                            "parent_id": {
                                "type": "string",
                                "label": "Parent Page/Database ID (Optional)",
                                "description": "ID of the parent page or database (UUID or full Notion URL). If not provided, page will be created in workspace root.",
                                "required": False,
                                "placeholder": "https://www.notion.so/MyPage-12345678-1234-1234-1234-123456789012 or 12345678-1234-1234-1234-123456789012",
                            },
                            "title": {
                                "type": "string",
                                "label": "Page Title",
                                "description": "Title of the new page",
                                "required": True,
                                "placeholder": "New Page Title",
                            },
                            "content": {
                                "type": "text",
                                "label": "Page Content",
                                "description": "Initial content for the page (optional)",
                                "required": False,
                                "placeholder": "Page content here...",
                            },
                        },
                    },
                    {
                        "name": "notion_update_page",
                        "description": "Update an existing Notion page",
                        "config_schema": {
                            "page_id": {
                                "type": "string",
                                "label": "Page",
                                "description": "Name of the page or full Notion page URL",
                                "required": True,
                                "placeholder": "My Page or https://www.notion.so/MyPage-12345678",
                            },
                            "title": {
                                "type": "string",
                                "label": "New Title",
                                "description": "New title for the page (optional)",
                                "required": False,
                                "placeholder": "Updated Page Title",
                            },
                            "content": {
                                "type": "text",
                                "label": "New Content",
                                "description": "New content to append (optional)",
                                "required": False,
                                "placeholder": "Additional content...",
                            },
                        },
                    },
                    {
                        "name": "notion_create_database_item",
                        "description": "Add a new item to a Notion database",
                        "config_schema": {
                            "database_id": {
                                "type": "string",
                                "label": "Database",
                                "description": "Name of the database or full Notion database URL",
                                "required": True,
                                "placeholder": "My Tasks Database or https://www.notion.so/MyDatabase-12345678-1234-1234-1234-123456789012",
                            },
                            "item_name": {
                                "type": "string",
                                "label": "Item Name",
                                "description": "Name/title of the new database item",
                                "required": True,
                                "placeholder": "New Task",
                            },
                            "properties": {
                                "type": "text",
                                "label": "Additional Properties",
                                "description": "Additional database properties as JSON object (optional)",
                                "required": False,
                                "placeholder": '{"Status": {"select": {"name": "To Do"}}, "Priority": {"select": {"name": "High"}}}',
                            },
                        },
                    },
                ],
            },
            {
                "name": "youtube",
                "description": "YouTube video integration for monitoring and interacting with videos",
                "status": Service.Status.ACTIVE,
                "actions": [
                    {
                        "name": "youtube_new_video",
                        "description": "Triggered when a new video is uploaded to a channel",
                        "config_schema": {
                            "channel_id": {
                                "type": "string",
                                "label": "Channel ID",
                                "description": "YouTube channel ID to monitor (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)",
                                "required": True,
                                "placeholder": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                            },
                        },
                    },
                    {
                        "name": "youtube_channel_stats",
                        "description": "Triggered when channel statistics change (subscribers, views)",
                        "config_schema": {
                            "channel_id": {
                                "type": "string",
                                "label": "Channel ID",
                                "description": "YouTube channel ID to monitor",
                                "required": True,
                                "placeholder": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                            },
                            "threshold_type": {
                                "type": "string",
                                "label": "Threshold Type",
                                "description": "Type of metric to monitor",
                                "required": True,
                                "default": "subscribers",
                                "enum": ["subscribers", "views", "videos"],
                            },
                            "threshold_value": {
                                "type": "number",
                                "label": "Threshold Value",
                                "description": "Trigger when metric exceeds this value",
                                "required": True,
                                "default": 1000,
                                "minimum": 0,
                            },
                        },
                    },
                    {
                        "name": "youtube_search_videos",
                        "description": "Triggered when new videos matching search criteria are found",
                        "config_schema": {
                            "search_query": {
                                "type": "string",
                                "label": "Search Query",
                                "description": "Keywords to search for in video titles and descriptions",
                                "required": True,
                                "placeholder": "python tutorial",
                            },
                            "channel_id": {
                                "type": "string",
                                "label": "Channel ID (Optional)",
                                "description": "Limit search to specific channel (optional)",
                                "required": False,
                                "placeholder": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                            },
                        },
                    },
                ],
                "reactions": [
                    {
                        "name": "youtube_post_comment",
                        "description": "Post a comment on a YouTube video",
                        "config_schema": {
                            "video_id": {
                                "type": "string",
                                "label": "Video ID",
                                "description": "YouTube video ID (automatically provided by trigger or enter manually)",
                                "required": True,
                                "default": "{video_id}",
                                "placeholder": "{video_id} or dQw4w9WgXcQ",
                            },
                            "comment_text": {
                                "type": "text",
                                "label": "Comment Text",
                                "description": "Text content of the comment (supports variables: {video_title}, {channel_name})",
                                "required": True,
                                "placeholder": "Great video! Thanks for sharing.",
                            },
                        },
                    },
                    {
                        "name": "youtube_add_to_playlist",
                        "description": "Add a video to a YouTube playlist",
                        "config_schema": {
                            "video_id": {
                                "type": "string",
                                "label": "Video ID",
                                "description": "YouTube video ID (automatically provided by trigger or enter manually)",
                                "required": True,
                                "default": "{video_id}",
                                "placeholder": "{video_id} or dQw4w9WgXcQ",
                            },
                            "playlist_id": {
                                "type": "string",
                                "label": "Playlist ID",
                                "description": "ID of the playlist to add video to",
                                "required": True,
                                "placeholder": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                            },
                        },
                    },
                    {
                        "name": "youtube_rate_video",
                        "description": "Like or dislike a YouTube video",
                        "config_schema": {
                            "video_id": {
                                "type": "string",
                                "label": "Video ID",
                                "description": "YouTube video ID (automatically provided by trigger or enter manually)",
                                "required": True,
                                "default": "{video_id}",
                                "placeholder": "{video_id} or dQw4w9WgXcQ",
                            },
                            "rating": {
                                "type": "string",
                                "label": "Rating",
                                "description": "Like, dislike, or remove rating",
                                "required": True,
                                "default": "like",
                                "enum": ["like", "dislike", "none"],
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
