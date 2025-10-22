##
## EPITECH PROJECT, 2025
## Area
## File description:
## twitch_helper
##

"""Twitch API helper functions for actions and reactions."""

import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

TWITCH_API_BASE = "https://api.twitch.tv/helix"


def _make_twitch_request(
    endpoint: str,
    access_token: str,
    client_id: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Dict:
    """
    Make a request to Twitch API.

    Args:
        endpoint: API endpoint (e.g., '/streams')
        access_token: Valid Twitch OAuth2 access token
        client_id: Twitch application client ID
        method: HTTP method (GET, POST, PATCH, DELETE)
        params: Query parameters
        json_data: JSON body for POST/PATCH requests

    Returns:
        Dict: JSON response from Twitch API

    Raises:
        requests.exceptions.HTTPError: If request fails
    """
    url = f"{TWITCH_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
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

    # Some endpoints return 204 No Content (e.g., whispers)
    if response.status_code == 204 or not response.content:
        return {}

    return response.json()


# ==================== User Information ====================


def get_user_info(access_token: str, client_id: str, user_login: Optional[str] = None) -> Dict:
    """
    Get user information by login or authenticated user.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        user_login: Optional username to lookup (default: authenticated user)

    Returns:
        Dict with user info: id, login, display_name, broadcaster_type, etc.

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    params = {}
    if user_login:
        params["login"] = user_login

    result = _make_twitch_request("/users", access_token, client_id, params=params)

    if not result.get("data"):
        raise ValueError("No user data returned from Twitch")

    return result["data"][0]


def get_user_by_id(access_token: str, client_id: str, user_id: str) -> Dict:
    """
    Get user information by user ID.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        user_id: Twitch user ID

    Returns:
        Dict with user info

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/users", access_token, client_id, params={"id": user_id}
    )

    if not result.get("data"):
        raise ValueError(f"User {user_id} not found")

    return result["data"][0]


# ==================== Stream Information ====================


def get_streams(
    access_token: str,
    client_id: str,
    user_id: Optional[str] = None,
    user_login: Optional[str] = None,
) -> List[Dict]:
    """
    Get information about active streams.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        user_id: Filter by user ID
        user_login: Filter by user login name

    Returns:
        List of stream data dicts

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    if user_login:
        params["user_login"] = user_login

    result = _make_twitch_request("/streams", access_token, client_id, params=params)
    return result.get("data", [])


def is_stream_live(access_token: str, client_id: str, user_id: str) -> bool:
    """
    Check if a user is currently streaming.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        user_id: Twitch user ID to check

    Returns:
        bool: True if streaming, False otherwise
    """
    streams = get_streams(access_token, client_id, user_id=user_id)
    return len(streams) > 0


def get_stream_info(access_token: str, client_id: str, user_id: str) -> Optional[Dict]:
    """
    Get current stream information for a user.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        user_id: Twitch user ID

    Returns:
        Dict with stream info or None if offline

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    streams = get_streams(access_token, client_id, user_id=user_id)
    return streams[0] if streams else None


# ==================== Channel Information ====================


def get_channel_info(access_token: str, client_id: str, broadcaster_id: str) -> Dict:
    """
    Get channel information.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID

    Returns:
        Dict with channel info: title, game_name, broadcaster_language, etc.

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/channels",
        access_token,
        client_id,
        params={"broadcaster_id": broadcaster_id},
    )

    if not result.get("data"):
        raise ValueError(f"Channel {broadcaster_id} not found")

    return result["data"][0]


def modify_channel_info(
    access_token: str,
    client_id: str,
    broadcaster_id: str,
    title: Optional[str] = None,
    game_id: Optional[str] = None,
    broadcaster_language: Optional[str] = None,
) -> bool:
    """
    Modify channel information (title, game, language).

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID
        title: New stream title
        game_id: New game/category ID
        broadcaster_language: Broadcaster language (e.g., 'en', 'fr')

    Returns:
        bool: True if successful

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    data = {}
    if title is not None:
        data["title"] = title
    if game_id is not None:
        data["game_id"] = game_id
    if broadcaster_language is not None:
        data["broadcaster_language"] = broadcaster_language

    _make_twitch_request(
        "/channels",
        access_token,
        client_id,
        method="PATCH",
        params={"broadcaster_id": broadcaster_id},
        json_data=data,
    )

    logger.info(f"Modified channel info for broadcaster {broadcaster_id}")
    return True


# ==================== Followers ====================


def get_followers(
    access_token: str,
    client_id: str,
    broadcaster_id: str,
    first: int = 20,
) -> List[Dict]:
    """
    Get a list of users who follow the specified broadcaster.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID
        first: Number of results to return (max 100)

    Returns:
        List of follower data dicts

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/channels/followers",
        access_token,
        client_id,
        params={"broadcaster_id": broadcaster_id, "first": min(first, 100)},
    )
    return result.get("data", [])


def get_follower_count(access_token: str, client_id: str, broadcaster_id: str) -> int:
    """
    Get total number of followers for a broadcaster.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID

    Returns:
        int: Total follower count

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/channels/followers",
        access_token,
        client_id,
        params={"broadcaster_id": broadcaster_id, "first": 1},
    )
    return result.get("total", 0)


# ==================== Subscriptions ====================


def get_broadcaster_subscriptions(
    access_token: str,
    client_id: str,
    broadcaster_id: str,
    first: int = 20,
) -> List[Dict]:
    """
    Get broadcaster's subscriber list.

    Args:
        access_token: Valid Twitch OAuth token (requires channel:read:subscriptions)
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID
        first: Number of results to return (max 100)

    Returns:
        List of subscription data dicts

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/subscriptions",
        access_token,
        client_id,
        params={"broadcaster_id": broadcaster_id, "first": min(first, 100)},
    )
    return result.get("data", [])


# ==================== Clips ====================


def create_clip(access_token: str, client_id: str, broadcaster_id: str) -> Dict:
    """
    Create a clip from the broadcaster's stream.

    Args:
        access_token: Valid Twitch OAuth token (requires clips:edit)
        client_id: Twitch application client ID
        broadcaster_id: Broadcaster's user ID

    Returns:
        Dict with clip info: id, edit_url

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/clips",
        access_token,
        client_id,
        method="POST",
        params={"broadcaster_id": broadcaster_id},
    )

    if not result.get("data"):
        raise ValueError("Failed to create clip")

    clip_data = result["data"][0]
    logger.info(f"Created clip {clip_data['id']} for broadcaster {broadcaster_id}")
    return clip_data


def get_clips(
    access_token: str,
    client_id: str,
    broadcaster_id: Optional[str] = None,
    game_id: Optional[str] = None,
    first: int = 20,
) -> List[Dict]:
    """
    Get clips for a broadcaster or game.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Filter by broadcaster ID
        game_id: Filter by game ID
        first: Number of results (max 100)

    Returns:
        List of clip data dicts

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    params = {"first": min(first, 100)}
    if broadcaster_id:
        params["broadcaster_id"] = broadcaster_id
    if game_id:
        params["game_id"] = game_id

    result = _make_twitch_request("/clips", access_token, client_id, params=params)
    return result.get("data", [])


# ==================== Chat ====================


def send_chat_message(
    access_token: str,
    client_id: str,
    broadcaster_id: str,
    sender_id: str,
    message: str,
) -> bool:
    """
    Send a chat message to a channel.

    Args:
        access_token: Valid Twitch OAuth token (requires chat:edit)
        client_id: Twitch application client ID
        broadcaster_id: Channel to send message to
        sender_id: User ID sending the message
        message: Message text to send

    Returns:
        bool: True if successful

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    data = {
        "broadcaster_id": broadcaster_id,
        "sender_id": sender_id,
        "message": message,
    }

    _make_twitch_request(
        "/chat/messages",
        access_token,
        client_id,
        method="POST",
        json_data=data,
    )

    logger.info(f"Sent chat message to channel {broadcaster_id}")
    return True


def send_whisper(
    access_token: str,
    client_id: str,
    from_user_id: str,
    to_user_id: str,
    message: str,
) -> bool:
    """
    Send a whisper (private message) to a Twitch user.

    Args:
        access_token: Valid Twitch OAuth token (requires user:manage:whispers)
        client_id: Twitch application client ID
        from_user_id: User ID sending the whisper
        to_user_id: User ID receiving the whisper
        message: Message text to send (max 500 characters)

    Returns:
        bool: True if successful

    Raises:
        requests.exceptions.HTTPError: If API call fails

    Note:
        - The sender must have a verified phone number
        - The sender's account must not be banned
        - Maximum 3 whispers per second, 100 per minute, 500 per hour
    """
    data = {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "message": message[:500],  # Limit to 500 characters
    }

    _make_twitch_request(
        "/whispers",
        access_token,
        client_id,
        method="POST",
        json_data=data,
    )

    logger.info(f"Sent whisper from {from_user_id} to {to_user_id}")
    return True


def send_chat_announcement(
    access_token: str,
    client_id: str,
    broadcaster_id: str,
    moderator_id: str,
    message: str,
    color: str = "primary",
) -> bool:
    """
    Send an announcement in chat.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        broadcaster_id: Channel to send announcement to
        moderator_id: Moderator user ID
        message: Announcement message
        color: Announcement color (primary, blue, green, orange, purple)

    Returns:
        bool: True if successful

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    data = {
        "message": message,
        "color": color,
    }

    _make_twitch_request(
        "/chat/announcements",
        access_token,
        client_id,
        method="POST",
        params={"broadcaster_id": broadcaster_id, "moderator_id": moderator_id},
        json_data=data,
    )

    logger.info(f"Sent announcement to channel {broadcaster_id}")
    return True


# ==================== Games/Categories ====================


def search_categories(
    access_token: str,
    client_id: str,
    query: str,
    first: int = 20,
) -> List[Dict]:
    """
    Search for game/category by name.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        query: Search query
        first: Number of results (max 100)

    Returns:
        List of category/game dicts with id, name, box_art_url

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/search/categories",
        access_token,
        client_id,
        params={"query": query, "first": min(first, 100)},
    )
    return result.get("data", [])


def get_top_games(
    access_token: str,
    client_id: str,
    first: int = 20,
) -> List[Dict]:
    """
    Get top games by viewer count.

    Args:
        access_token: Valid Twitch OAuth token
        client_id: Twitch application client ID
        first: Number of results (max 100)

    Returns:
        List of game dicts

    Raises:
        requests.exceptions.HTTPError: If API call fails
    """
    result = _make_twitch_request(
        "/games/top",
        access_token,
        client_id,
        params={"first": min(first, 100)},
    )
    return result.get("data", [])
