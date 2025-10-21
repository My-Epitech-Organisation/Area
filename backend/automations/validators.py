"""
Schema validation utilities for AREA actions and reactions.

This module defines JSON schemas for validating action_config and reaction_config
based on the specific action or reaction type.
"""

import re

import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError
from rest_framework import serializers


def validate_email_format(email):
    """Simple email validation function."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None


# JSON Schemas pour les Actions
ACTION_SCHEMAS = {
    "timer_daily": {
        "type": "object",
        "properties": {
            "hour": {
                "type": "integer",
                "minimum": 0,
                "maximum": 23,
                "description": "Hour of the day (0-23)",
            },
            "minute": {
                "type": "integer",
                "minimum": 0,
                "maximum": 59,
                "description": "Minute of the hour (0-59)",
            },
            "timezone": {
                "type": "string",
                "default": "UTC",
                "description": "Timezone for the schedule",
            },
        },
        "required": ["hour", "minute"],
        "additionalProperties": False,
    },
    "timer_weekly": {
        "type": "object",
        "properties": {
            "day_of_week": {
                "type": "integer",
                "minimum": 0,
                "maximum": 6,
                "description": "Day of week (0=Monday, 6=Sunday)",
            },
            "hour": {"type": "integer", "minimum": 0, "maximum": 23},
            "minute": {"type": "integer", "minimum": 0, "maximum": 59},
            "timezone": {"type": "string", "default": "UTC"},
        },
        "required": ["day_of_week", "hour", "minute"],
        "additionalProperties": False,
    },
    "github_new_issue": {
        "type": "object",
        "properties": {
            "repository": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$",
                "description": "Repository in format owner/repo",
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by issue labels (optional)",
            },
        },
        "required": ["repository"],
        "additionalProperties": False,
    },
    "github_new_pr": {
        "type": "object",
        "properties": {
            "repository": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$",
            },
            "branch": {
                "type": "string",
                "description": "Target branch (optional, default: main)",
            },
        },
        "required": ["repository"],
        "additionalProperties": False,
    },
    "gmail_new_email": {
        "type": "object",
        "properties": {
            "from_email": {
                "type": "string",
                "format": "email",
                "description": "Filter emails from specific sender (optional)",
            },
            "subject_contains": {
                "type": "string",
                "description": "Filter emails with subject containing text (optional)",
            },
            "has_attachment": {
                "type": "boolean",
                "description": "Filter emails with attachments (optional)",
            },
        },
        "additionalProperties": False,
    },
    "gmail_new_from_sender": {
        "type": "object",
        "properties": {
            "from_email": {
                "type": "string",
                "format": "email",
                "description": "Email sender to monitor",
            },
        },
        "required": ["from_email"],
        "additionalProperties": False,
    },
    "gmail_new_with_label": {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "minLength": 1,
                "description": "Gmail label to monitor",
            },
        },
        "required": ["label"],
        "additionalProperties": False,
    },
    "gmail_new_with_subject": {
        "type": "object",
        "properties": {
            "subject_contains": {
                "type": "string",
                "minLength": 1,
                "description": "Text that must appear in subject",
            },
        },
        "required": ["subject_contains"],
        "additionalProperties": False,
    },
    "calendar_event_starting_soon": {
        "type": "object",
        "properties": {
            "minutes_before": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1440,
                "default": 15,
                "description": "Minutes before event to trigger (1-1440)",
            },
        },
        "required": ["minutes_before"],
        "additionalProperties": False,
    },
    "calendar_new_event": {
        "type": "object",
        "properties": {
            "calendar_id": {
                "type": "string",
                "description": "Specific calendar ID to monitor (optional, defaults to primary)",
            },
        },
        "additionalProperties": False,
    },
    "webhook_trigger": {
        "type": "object",
        "properties": {
            "webhook_url": {
                "type": "string",
                "format": "uri",
                "description": "Webhook endpoint URL",
            },
            "secret": {
                "type": "string",
                "minLength": 8,
                "description": "Webhook secret for signature validation",
            },
            "method": {"type": "string", "enum": ["POST", "PUT"], "default": "POST"},
        },
        "required": ["webhook_url"],
        "additionalProperties": False,
    },
    "weather_condition_met": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Location to monitor (city name or coordinates)",
            },
            "condition": {
                "type": "string",
                "enum": ["rain", "snow", "temperature_above", "temperature_below"],
                "description": "Weather condition to trigger on",
            },
            "threshold": {
                "type": "number",
                "description": "Temperature threshold (required for temperature conditions)",
            },
        },
        "required": ["location", "condition"],
        "additionalProperties": False,
    },
}


# JSON Schemas pour les Reactions
REACTION_SCHEMAS = {
    "send_email": {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "format": "email",
                "description": "Email recipient",
            },
            "subject": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Email subject",
            },
            "body": {
                "type": "string",
                "description": "Email body (can contain template variables)",
            },
            "template_vars": {
                "type": "object",
                "description": "Variables to replace in body template",
            },
        },
        "required": ["recipient", "subject"],
        "additionalProperties": False,
    },
    "slack_message": {
        "type": "object",
        "properties": {
            "channel": {
                "type": "string",
                "pattern": "^#?[a-zA-Z0-9._-]+$",
                "description": "Slack channel name (with or without #)",
            },
            "message": {
                "type": "string",
                "minLength": 1,
                "maxLength": 4000,
                "description": "Message content",
            },
            "username": {"type": "string", "description": "Bot username (optional)"},
            "icon_emoji": {
                "type": "string",
                "pattern": "^:[a-zA-Z0-9._+-]+:$",
                "description": "Bot emoji icon (optional)",
            },
        },
        "required": ["channel", "message"],
        "additionalProperties": False,
    },
    "teams_message": {
        "type": "object",
        "properties": {
            "webhook_url": {
                "type": "string",
                "format": "uri",
                "pattern": "https://[a-zA-Z0-9.-]+\\.webhook\\.office\\.com/",
                "description": "Teams webhook URL",
            },
            "title": {
                "type": "string",
                "maxLength": 150,
                "description": "Message title",
            },
            "text": {
                "type": "string",
                "minLength": 1,
                "description": "Message content",
            },
            "color": {
                "type": "string",
                "pattern": "^#[0-9A-Fa-f]{6}$",
                "default": "#0078D4",
                "description": "Message color theme",
            },
        },
        "required": ["webhook_url", "text"],
        "additionalProperties": False,
    },
    "github_create_issue": {
        "type": "object",
        "properties": {
            "repository": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$",
            },
            "title": {"type": "string", "minLength": 1, "maxLength": 200},
            "body": {"type": "string", "description": "Issue description"},
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Issue labels",
            },
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "GitHub usernames to assign",
            },
        },
        "required": ["repository", "title"],
        "additionalProperties": False,
    },
    "save_to_dropbox": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "pattern": "^/.*",
                "description": "Dropbox folder path (must start with /)",
            },
            "filename": {
                "type": "string",
                "description": "File name (can contain template variables)",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Overwrite existing file",
            },
        },
        "required": ["folder_path", "filename"],
        "additionalProperties": False,
    },
    # Gmail Reactions
    "gmail_send_email": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "format": "email",
                "description": "Recipient email address",
            },
            "subject": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Email subject",
            },
            "body": {
                "type": "string",
                "minLength": 1,
                "description": "Email body content",
            },
        },
        "required": ["to", "subject", "body"],
        "additionalProperties": False,
    },
    "gmail_mark_read": {
        "type": "object",
        "properties": {
            "email_id": {
                "type": "string",
                "description": "Gmail message ID to mark as read",
            },
        },
        "required": ["email_id"],
        "additionalProperties": False,
    },
    "gmail_add_label": {
        "type": "object",
        "properties": {
            "email_id": {
                "type": "string",
                "description": "Gmail message ID",
            },
            "label": {
                "type": "string",
                "minLength": 1,
                "description": "Label name to add",
            },
        },
        "required": ["email_id", "label"],
        "additionalProperties": False,
    },
    # Google Calendar Reactions
    "calendar_create_event": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Event title/summary",
            },
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "Event start time (ISO 8601)",
            },
            "end_time": {
                "type": "string",
                "format": "date-time",
                "description": "Event end time (ISO 8601)",
            },
            "description": {
                "type": "string",
                "description": "Event description (optional)",
            },
            "location": {
                "type": "string",
                "description": "Event location (optional)",
            },
        },
        "required": ["summary", "start_time", "end_time"],
        "additionalProperties": False,
    },
    "calendar_update_event": {
        "type": "object",
        "properties": {
            "event_id": {
                "type": "string",
                "description": "Calendar event ID to update",
            },
            "summary": {
                "type": "string",
                "maxLength": 200,
                "description": "New event title (optional)",
            },
            "start_time": {
                "type": "string",
                "format": "date-time",
                "description": "New start time (optional)",
            },
            "end_time": {
                "type": "string",
                "format": "date-time",
                "description": "New end time (optional)",
            },
            "description": {
                "type": "string",
                "description": "New event description (optional)",
            },
        },
        "required": ["event_id"],
        "additionalProperties": False,
    },
    "log_message": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "minLength": 1,
                "description": "Log message content",
            },
            "level": {
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
                "default": "INFO",
                "description": "Log level",
            },
            "include_payload": {
                "type": "boolean",
                "default": True,
                "description": "Include action payload in log",
            },
        },
        "required": ["message"],
        "additionalProperties": False,
    },
    "webhook_post": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "format": "uri",
                "description": "Target webhook URL to POST to",
            },
            "method": {
                "type": "string",
                "enum": ["POST", "PUT", "PATCH"],
                "default": "POST",
                "description": "HTTP method to use",
            },
            "headers": {
                "type": "object",
                "description": "Custom HTTP headers (optional)",
                "additionalProperties": {"type": "string"},
            },
            "body": {
                "type": "string",
                "description": "Request body (can contain template variables)",
            },
        },
        "required": ["url"],
        "additionalProperties": False,
    },
    "weather_send_alert": {
        "type": "object",
        "properties": {
            "alert_method": {
                "type": "string",
                "enum": ["email", "slack", "teams"],
                "description": "Method to send alert",
            },
            "recipient": {
                "type": "string",
                "description": "Recipient (email address or channel/webhook URL)",
            },
            "message": {
                "type": "string",
                "minLength": 1,
                "description": "Alert message content",
            },
        },
        "required": ["alert_method", "recipient", "message"],
        "additionalProperties": False,
    },
}


# Règles de compatibilité Action -> Reaction
COMPATIBILITY_RULES = {
    # Timer actions peuvent déclencher n'importe quelle reaction
    "timer_daily": ["*"],  # * signifie toutes les reactions
    "timer_weekly": ["*"],
    # GitHub actions
    "github_new_issue": [
        "send_email",
        "gmail_send_email",
        "slack_message",
        "teams_message",
        "log_message",
        "webhook_post",
        "calendar_create_event",
    ],
    "github_new_pr": [
        "send_email",
        "gmail_send_email",
        "slack_message",
        "teams_message",
        "log_message",
        "webhook_post",
        "calendar_create_event",
    ],
    # Gmail actions - can trigger most reactions except email to avoid loops
    "gmail_new_email": [
        "save_to_dropbox",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
        "calendar_create_event",
        "gmail_mark_read",
        "gmail_add_label",
    ],
    "gmail_new_from_sender": [
        "save_to_dropbox",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
        "calendar_create_event",
        "gmail_mark_read",
        "gmail_add_label",
    ],
    "gmail_new_with_label": [
        "save_to_dropbox",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
        "calendar_create_event",
        "gmail_mark_read",
        "gmail_add_label",
    ],
    "gmail_new_with_subject": [
        "save_to_dropbox",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
        "calendar_create_event",
        "gmail_mark_read",
        "gmail_add_label",
    ],
    # Google Calendar actions
    "calendar_event_starting_soon": [
        "send_email",
        "gmail_send_email",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
    ],
    "calendar_new_event": [
        "send_email",
        "gmail_send_email",
        "slack_message",
        "teams_message",
        "github_create_issue",
        "log_message",
        "webhook_post",
    ],
    # Webhook actions can trigger anything
    "webhook_trigger": ["*"],
    # Weather actions
    "weather_condition_met": [
        "send_email",
        "gmail_send_email",
        "slack_message",
        "teams_message",
        "log_message",
        "webhook_post",
        "weather_send_alert",
    ],
}


def validate_action_config(action_name, config):
    """
    Validate action configuration against its schema.

    Args:
        action_name (str): Name of the action
        config (dict): Configuration to validate

    Raises:
        serializers.ValidationError: If validation fails
    """
    if not config:
        config = {}

    schema = ACTION_SCHEMAS.get(action_name)
    if not schema:
        # No defined pattern, basic validation only
        if not isinstance(config, dict):
            raise serializers.ValidationError(
                f"Configuration for action '{action_name}' must be a JSON object."
            )
        return

    try:
        jsonschema.validate(config, schema)
    except JsonSchemaValidationError as e:
        raise serializers.ValidationError(
            f"Invalid configuration for action '{action_name}': {e.message}"
        )


def validate_reaction_config(reaction_name, config):
    """
    Validate reaction configuration against its schema.

    Args:
        reaction_name (str): Name of the reaction
        config (dict): Configuration to validate

    Raises:
        serializers.ValidationError: If validation fails
    """
    if not config:
        config = {}

    schema = REACTION_SCHEMAS.get(reaction_name)
    if not schema:
        # No defined pattern, basic validation only
        if not isinstance(config, dict):
            raise serializers.ValidationError(
                f"Configuration for reaction '{reaction_name}' must be a JSON object."
            )
        return

    try:
        jsonschema.validate(config, schema)

        # Additional validation for emails
        if reaction_name == "send_email" and "recipient" in config:
            if not validate_email_format(config["recipient"]):
                raise serializers.ValidationError(
                    f"Invalid email format for recipient: {config['recipient']}"
                )

    except JsonSchemaValidationError as e:
        raise serializers.ValidationError(
            f"Invalid configuration for reaction '{reaction_name}': {e.message}"
        )


def validate_action_reaction_compatibility(action_name, reaction_name):
    """
    Validate that an action can trigger a specific reaction.

    Args:
        action_name (str): Name of the action
        reaction_name (str): Name of the reaction

    Raises:
        serializers.ValidationError: If action and reaction are not compatible
    """
    compatible_reactions = COMPATIBILITY_RULES.get(action_name, [])

    # If '*' in the list, all reactions are allowed
    if "*" in compatible_reactions:
        return

    # Check if the specific reaction is allowed
    if reaction_name not in compatible_reactions:
        raise serializers.ValidationError(
            f"Action '{action_name}' is not compatible with reaction '{reaction_name}'. "
            f"Compatible reactions: {', '.join(compatible_reactions)}"
        )


def get_action_schema(action_name):
    """Get the JSON schema for an action."""
    return ACTION_SCHEMAS.get(action_name)


def get_reaction_schema(reaction_name):
    """Get the JSON schema for a reaction."""
    return REACTION_SCHEMAS.get(reaction_name)


def get_compatible_reactions(action_name):
    """Get list of compatible reactions for an action."""
    return COMPATIBILITY_RULES.get(action_name, [])
