"""
Webhook-related constants for event types and mappings.

Centralizes webhook event definitions to avoid duplication across the codebase.
"""

# Supported webhook events by service
SUPPORTED_WEBHOOK_EVENTS = {
    "github": ["issues", "pull_request", "push", "issue_comment", "star"],
    "twitch": [
        "stream.online",
        "stream.offline",
        "channel.follow",
        "channel.subscribe",
        "channel.update",
    ],
    "slack": ["message", "app_mention", "member_joined_channel"],
    "gmail": ["message", "email_received"],
    "notion": [
        "page.created",
        "page.updated",
        "page.deleted",
        "database.created",
        "database.updated",
        "database.deleted",
    ],
}

# Mapping of webhook event types to internal action names
WEBHOOK_EVENT_TO_ACTION = {
    "github": {
        "issues": "github_issue",
        "pull_request": "github_pull_request",
        "push": "github_push",
        "issue_comment": "github_issue_comment",
        "star": "github_star",
    },
    "twitch": {
        "stream.online": "twitch_stream_online",
        "stream.offline": "twitch_stream_offline",
        "channel.follow": "twitch_follow",
        "channel.subscribe": "twitch_subscribe",
        "channel.update": "twitch_stream_update",
    },
    "slack": {
        "message": "slack_message",
        "app_mention": "slack_app_mention",
        "member_joined_channel": "slack_member_joined",
    },
    "gmail": {
        "message": "gmail_received",
        "email_received": "gmail_received",
    },
    "notion": {
        "page.created": "notion_page_created",
        "page.properties_updated": "notion_page_updated",
        "page.content_updated": "notion_page_updated",
        "page.deleted": "notion_page_deleted",
        "database.content_updated": "notion_database_item_added",  # New item = content update
        "database.deleted": "notion_database_deleted",
        # Legacy support for simplified event names
        "page": "notion_page_updated",
        "database": "notion_database_item_added",
    },
}
