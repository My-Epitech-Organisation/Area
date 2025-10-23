##
## EPITECH PROJECT, 2025
## Area
## File description:
## slack_helper
##

"""Slack API helper functions for actions and reactions."""

import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

SLACK_API_BASE = "https://slack.com/api"


def _make_slack_request(
    endpoint: str,
    access_token: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Dict:
    """
    Make a request to Slack API.

    Args:
        endpoint: API endpoint (e.g., '/chat.postMessage')
        access_token: Valid Slack OAuth2 access token
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        json_data: JSON body for POST requests

    Returns:
        Dict: JSON response from Slack API

    Raises:
        requests.exceptions.HTTPError: If request fails
    """
    url = f"{SLACK_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json_data,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    # Check for Slack API errors
    if not result.get("ok"):
        error_msg = result.get("error", "Unknown Slack API error")
        raise ValueError(f"Slack API error: {error_msg}")

    return result


# ==================== Channel Management ====================


def list_channels(access_token: str, types: str = "public_channel") -> List[Dict]:
    """
    List Slack channels accessible to the user.

    Args:
        access_token: Valid Slack access token
        types: Types of channels to list (public_channel, private_channel, im, mpim)

    Returns:
        List of channel dicts with id, name, is_channel, etc.

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        result = _make_slack_request(
            "/conversations.list",
            access_token,
            params={
                "types": types,
                "limit": 200,  # Max 200 channels
            },
        )

        channels = result.get("channels", [])
        logger.info(f"Found {len(channels)} Slack channels")
        return channels

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack list_channels failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_channels: {e}")
        raise


def get_channel_info(access_token: str, channel_id: str) -> Dict:
    """
    Get information about a specific Slack channel.

    Args:
        access_token: Valid Slack access token
        channel_id: Slack channel ID

    Returns:
        Dict with channel information

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        result = _make_slack_request(
            "/conversations.info",
            access_token,
            params={"channel": channel_id},
        )

        channel = result.get("channel", {})
        logger.info(
            f"Retrieved info for Slack channel: {channel.get('name', channel_id)}"
        )
        return channel

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack get_channel_info failed for {channel_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_info: {e}")
        raise


def find_channel_by_name(access_token: str, channel_name: str) -> Optional[Dict]:
    """
    Find a channel by name (with or without # prefix).

    Args:
        access_token: Valid Slack access token
        channel_name: Channel name to search for

    Returns:
        Channel dict if found, None otherwise
    """
    # Remove # prefix if present
    clean_name = channel_name.lstrip("#")

    channels = list_channels(access_token, "public_channel,private_channel")

    for channel in channels:
        if channel.get("name") == clean_name:
            return channel

    return None


# ==================== Message Management ====================


def post_message(
    access_token: str,
    channel: str,
    text: str,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
    thread_ts: Optional[str] = None,
) -> Dict:
    """
    Post a message to a Slack channel.

    Args:
        access_token: Valid Slack access token
        channel: Channel ID or name (with or without #)
        text: Message text
        username: Bot username (optional)
        icon_emoji: Bot emoji icon (optional)
        thread_ts: Thread timestamp to reply in thread (optional)

    Returns:
        Dict with message details including ts (timestamp)

    Raises:
        ValueError: If Slack API returns an error or channel not found
    """
    try:
        # If channel is a name, find the channel ID
        if not channel.startswith(("C", "G", "D")):  # Not a channel ID
            channel_info = find_channel_by_name(access_token, channel)
            if not channel_info:
                raise ValueError(f"Channel '{channel}' not found")
            channel = channel_info["id"]

        # Prepare message payload
        payload = {
            "channel": channel,
            "text": text,
        }

        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if thread_ts:
            payload["thread_ts"] = thread_ts

        result = _make_slack_request(
            "/chat.postMessage", access_token, method="POST", json_data=payload
        )

        logger.info(f"Posted Slack message to {channel}: {text[:50]}...")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack post_message failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in post_message: {e}")
        raise


def get_channel_history(
    access_token: str,
    channel: str,
    limit: int = 100,
    oldest: Optional[str] = None,
) -> List[Dict]:
    """
    Get recent messages from a Slack channel.

    Args:
        access_token: Valid Slack access token
        channel: Channel ID or name
        limit: Maximum number of messages to return
        oldest: Only return messages after this timestamp

    Returns:
        List of message dicts

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        # If channel is a name, find the channel ID
        if not channel.startswith(("C", "G", "D")):  # Not a channel ID
            channel_info = find_channel_by_name(access_token, channel)
            if not channel_info:
                raise ValueError(f"Channel '{channel}' not found")
            channel = channel_info["id"]

        params = {
            "channel": channel,
            "limit": min(limit, 200),  # Slack max is 200
        }

        if oldest:
            params["oldest"] = oldest

        result = _make_slack_request(
            "/conversations.history", access_token, params=params
        )

        messages = result.get("messages", [])
        logger.info(f"Retrieved {len(messages)} messages from Slack channel {channel}")
        return messages

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack get_channel_history failed for {channel}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_history: {e}")
        raise


def search_messages(
    access_token: str,
    query: str,
    count: int = 20,
    sort: str = "timestamp",
) -> Dict:
    """
    Search for messages in Slack.

    Args:
        access_token: Valid Slack access token
        query: Search query
        count: Number of results to return
        sort: Sort order (timestamp, score)

    Returns:
        Dict with search results

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        result = _make_slack_request(
            "/search.messages",
            access_token,
            params={
                "query": query,
                "count": min(count, 100),  # Slack max is 100
                "sort": sort,
            },
        )

        messages = result.get("messages", {}).get("matches", [])
        logger.info(f"Found {len(messages)} Slack messages matching '{query}'")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack search_messages failed for query '{query}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_messages: {e}")
        raise


# ==================== User Management ====================


def list_users(access_token: str) -> List[Dict]:
    """
    List all users in the Slack workspace.

    Args:
        access_token: Valid Slack access token

    Returns:
        List of user dicts

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        result = _make_slack_request("/users.list", access_token)

        users = result.get("members", [])
        logger.info(f"Found {len(users)} Slack users")
        return users

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack list_users failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_users: {e}")
        raise


def get_user_info(access_token: str, user_id: str) -> Dict:
    """
    Get information about a specific Slack user.

    Args:
        access_token: Valid Slack access token
        user_id: Slack user ID

    Returns:
        Dict with user information

    Raises:
        ValueError: If Slack API returns an error
    """
    try:
        result = _make_slack_request(
            "/users.info",
            access_token,
            params={"user": user_id},
        )

        user = result.get("user", {})
        logger.info(f"Retrieved info for Slack user: {user.get('name', user_id)}")
        return user

    except requests.exceptions.RequestException as e:
        logger.error(f"Slack get_user_info failed for {user_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_user_info: {e}")
        raise


def find_user_by_name(access_token: str, username: str) -> Optional[Dict]:
    """
    Find a user by username.

    Args:
        access_token: Valid Slack access token
        username: Username to search for (without @)

    Returns:
        User dict if found, None otherwise
    """
    users = list_users(access_token)

    for user in users:
        if user.get("name") == username or user.get("real_name") == username:
            return user

    return None


# ==================== Event Processing ====================


def parse_message_event(event_data: Dict) -> Dict:
    """
    Parse a Slack message event into a standardized format.

    Args:
        event_data: Raw Slack event data

    Returns:
        Dict with parsed message information
    """
    message = {
        "type": event_data.get("type"),
        "channel": event_data.get("channel"),
        "user": event_data.get("user"),
        "text": event_data.get("text", ""),
        "timestamp": event_data.get("ts"),
        "thread_ts": event_data.get("thread_ts"),
        "channel_type": event_data.get("channel_type"),
    }

    # Add subtype if present (e.g., "bot_message", "channel_join")
    if "subtype" in event_data:
        message["subtype"] = event_data["subtype"]

    # Add bot info if present
    if "bot_id" in event_data:
        message["bot_id"] = event_data["bot_id"]
        message["bot_profile"] = event_data.get("bot_profile", {})

    return message


def is_user_mention(text: str, user_id: str) -> bool:
    """
    Check if a message mentions a specific user.

    Args:
        text: Message text
        user_id: Slack user ID to check for

    Returns:
        True if user is mentioned, False otherwise
    """
    return f"<@{user_id}>" in text


def extract_mentions(text: str) -> List[str]:
    """
    Extract all user mentions from a message.

    Args:
        text: Message text

    Returns:
        List of mentioned user IDs
    """
    import re

    # Find all patterns like <@U1234567890>
    mention_pattern = r"<@([U][A-Z0-9]+)>"
    matches = re.findall(mention_pattern, text)
    return matches
