##
## EPITECH PROJECT, 2025
## Area
## File description:
## spotify_helper
##

"""Spotify API helper functions for reactions."""

import logging
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

SPOTIFY_API_BASE = "https://api.spotify.com/v1"


def _make_spotify_request(
    endpoint: str,
    access_token: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Dict:
    """
    Make a request to Spotify Web API.

    Args:
        endpoint: API endpoint (e.g., '/me/player')
        access_token: Valid Spotify OAuth2 access token
        method: HTTP method (GET, POST, PUT, etc.)
        params: Query parameters
        json_data: JSON body for POST/PUT requests

    Returns:
        Dict: JSON response from Spotify API

    Raises:
        requests.exceptions.HTTPError: If request fails
        ValueError: If Spotify API returns an error
    """
    url = f"{SPOTIFY_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {access_token}",
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

    # Handle different response codes
    if response.status_code == 204:  # No Content (success for some operations)
        return {}

    response.raise_for_status()

    # For some endpoints, Spotify returns empty response on success
    if not response.content:
        return {}

    result = response.json()

    # Check for Spotify API errors (some errors return 200 with error in JSON)
    if isinstance(result, dict) and "error" in result:
        error_info = result["error"]
        if isinstance(error_info, dict):
            error_msg = error_info.get("message", "Unknown Spotify API error")
            error_code = error_info.get("status", response.status_code)
        else:
            error_msg = str(error_info)
            error_code = response.status_code

        raise ValueError(f"Spotify API error ({error_code}): {error_msg}")

    return result


# ==================== User Profile ====================


def get_current_user(access_token: str) -> Dict:
    """
    Get the current user's profile information.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with user profile information

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        result = _make_spotify_request("/me", access_token)
        logger.info(f"Retrieved Spotify user profile: {result.get('id')}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify get_current_user failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise


# ==================== Playback Control ====================


def get_current_playback(access_token: str) -> Optional[Dict]:
    """
    Get information about the user's current playback state.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with playback information, or None if nothing is playing

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        result = _make_spotify_request("/me/player", access_token)

        if not result:  # No active playback
            logger.info("No active Spotify playback found")
            return None

        logger.info(
            f"Retrieved current Spotify playback: {result.get('is_playing', False)}"
        )
        return result

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 204:  # No active playback
            logger.info("No active Spotify playback (204 response)")
            return None
        logger.error(f"Spotify get_current_playback failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_playback: {e}")
        raise


def play_track(access_token: str, track_uri: str, position_ms: int = 0) -> Dict:
    """
    Start playback of a specific track.

    Args:
        access_token: Valid Spotify access token
        track_uri: Spotify URI of the track (spotify:track:...)
        position_ms: Position to start playing from in milliseconds

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        payload = {
            "uris": [track_uri],
            "position_ms": position_ms,
        }

        _make_spotify_request(
            "/me/player/play",
            access_token,
            method="PUT",
            json_data=payload,
        )

        logger.info(f"Started Spotify playback: {track_uri}")
        return {"success": True, "track_uri": track_uri, "position_ms": position_ms}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify play_track failed for {track_uri}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in play_track: {e}")
        raise


def pause_playback(access_token: str) -> Dict:
    """
    Pause the current playback.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        _make_spotify_request("/me/player/pause", access_token, method="PUT")

        logger.info("Paused Spotify playback")
        return {"success": True}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify pause_playback failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in pause_playback: {e}")
        raise


def resume_playback(access_token: str) -> Dict:
    """
    Resume the current playback.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        _make_spotify_request("/me/player/play", access_token, method="PUT")

        logger.info("Resumed Spotify playback")
        return {"success": True}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify resume_playback failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in resume_playback: {e}")
        raise


def skip_to_next(access_token: str) -> Dict:
    """
    Skip to the next track in the queue.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        _make_spotify_request("/me/player/next", access_token, method="POST")

        logger.info("Skipped to next Spotify track")
        return {"success": True}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify skip_to_next failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in skip_to_next: {e}")
        raise


def skip_to_previous(access_token: str) -> Dict:
    """
    Skip to the previous track.

    Args:
        access_token: Valid Spotify access token

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        _make_spotify_request("/me/player/previous", access_token, method="POST")

        logger.info("Skipped to previous Spotify track")
        return {"success": True}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify skip_to_previous failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in skip_to_previous: {e}")
        raise


def set_volume(access_token: str, volume_percent: int) -> Dict:
    """
    Set the playback volume.

    Args:
        access_token: Valid Spotify access token
        volume_percent: Volume level as percentage (0-100)

    Returns:
        Dict with operation result

    Raises:
        ValueError: If volume_percent is invalid or Spotify API returns an error
    """
    try:
        if not (0 <= volume_percent <= 100):
            raise ValueError(f"Volume must be between 0 and 100, got {volume_percent}")

        _make_spotify_request(
            "/me/player/volume",
            access_token,
            method="PUT",
            params={"volume_percent": volume_percent},
        )

        logger.info(f"Set Spotify volume to {volume_percent}%")
        return {"success": True, "volume_percent": volume_percent}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify set_volume failed for {volume_percent}%: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in set_volume: {e}")
        raise


# ==================== Track Management ====================


def like_track(access_token: str, track_id: Optional[str] = None) -> Dict:
    """
    Like (save) a track to the user's library.

    Args:
        access_token: Valid Spotify access token
        track_id: Spotify track ID (if None, uses currently playing track)

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        if track_id is None:
            # Get currently playing track
            playback = get_current_playback(access_token)
            if not playback or not playback.get("item"):
                raise ValueError("No track currently playing")

            track_id = playback["item"]["id"]

        _make_spotify_request(
            f"/me/tracks?ids={track_id}",
            access_token,
            method="PUT",
        )

        logger.info(f"Liked Spotify track: {track_id}")
        return {"success": True, "track_id": track_id}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify like_track failed for {track_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in like_track: {e}")
        raise


def unlike_track(access_token: str, track_id: Optional[str] = None) -> Dict:
    """
    Unlike (unsave) a track from the user's library.

    Args:
        access_token: Valid Spotify access token
        track_id: Spotify track ID (if None, uses currently playing track)

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        if track_id is None:
            # Get currently playing track
            playback = get_current_playback(access_token)
            if not playback or not playback.get("item"):
                raise ValueError("No track currently playing")

            track_id = playback["item"]["id"]

        _make_spotify_request(
            f"/me/tracks?ids={track_id}",
            access_token,
            method="DELETE",
        )

        logger.info(f"Unliked Spotify track: {track_id}")
        return {"success": True, "track_id": track_id}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify unlike_track failed for {track_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in unlike_track: {e}")
        raise


def add_to_playlist(
    access_token: str, playlist_id: str, track_uri: Optional[str] = None
) -> Dict:
    """
    Add a track to a playlist.

    Args:
        access_token: Valid Spotify access token
        playlist_id: Spotify playlist ID
        track_uri: Spotify track URI (if None, uses currently playing track)

    Returns:
        Dict with operation result

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        if track_uri is None:
            # Get currently playing track
            playback = get_current_playback(access_token)
            if not playback or not playback.get("item"):
                raise ValueError("No track currently playing")

            track_uri = playback["item"]["uri"]

        # Ensure track_uri is in correct format
        if not track_uri.startswith("spotify:track:"):
            track_uri = f"spotify:track:{track_uri}"

        _make_spotify_request(
            f"/playlists/{playlist_id}/tracks",
            access_token,
            method="POST",
            json_data={"uris": [track_uri]},
        )

        logger.info(f"Added track {track_uri} to Spotify playlist {playlist_id}")
        return {"success": True, "playlist_id": playlist_id, "track_uri": track_uri}

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify add_to_playlist failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_to_playlist: {e}")
        raise


# ==================== Playlist Management ====================


def create_playlist(
    access_token: str, name: str, description: str = "", public: bool = False
) -> Dict:
    """
    Create a new playlist for the current user.

    Args:
        access_token: Valid Spotify access token
        name: Name for the new playlist
        description: Optional description
        public: Whether the playlist should be public

    Returns:
        Dict with playlist information

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        # Get current user ID
        user = get_current_user(access_token)
        user_id = user["id"]

        payload = {
            "name": name,
            "description": description,
            "public": public,
        }

        result = _make_spotify_request(
            f"/users/{user_id}/playlists",
            access_token,
            method="POST",
            json_data=payload,
        )

        logger.info(f"Created Spotify playlist: {name} (ID: {result.get('id')})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify create_playlist failed for '{name}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_playlist: {e}")
        raise


def get_user_playlists(access_token: str, limit: int = 50) -> List[Dict]:
    """
    Get the current user's playlists.

    Args:
        access_token: Valid Spotify access token
        limit: Maximum number of playlists to return

    Returns:
        List of playlist dicts

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        result = _make_spotify_request(
            "/me/playlists",
            access_token,
            params={"limit": min(limit, 50)},  # Spotify max is 50
        )

        playlists = result.get("items", [])
        logger.info(f"Retrieved {len(playlists)} Spotify playlists")
        return playlists

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify get_user_playlists failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_user_playlists: {e}")
        raise


# ==================== Track Information ====================


def get_track_info(access_token: str, track_id: str) -> Dict:
    """
    Get detailed information about a track.

    Args:
        access_token: Valid Spotify access token
        track_id: Spotify track ID

    Returns:
        Dict with track information

    Raises:
        ValueError: If Spotify API returns an error
    """
    try:
        result = _make_spotify_request(f"/tracks/{track_id}", access_token)

        logger.info(f"Retrieved Spotify track info: {result.get('name', track_id)}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Spotify get_track_info failed for {track_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_track_info: {e}")
        raise


# ==================== Event Processing ====================


def parse_playback_event(event_data: Dict) -> Dict:
    """
    Parse Spotify playback event into a standardized format.

    Args:
        event_data: Raw Spotify playback data

    Returns:
        Dict with parsed playback information
    """
    item = event_data.get("item", {})

    parsed = {
        "is_playing": event_data.get("is_playing", False),
        "progress_ms": event_data.get("progress_ms", 0),
        "timestamp": event_data.get("timestamp", 0),
        "device": event_data.get("device", {}),
        "shuffle_state": event_data.get("shuffle_state", False),
        "repeat_state": event_data.get("repeat_state", "off"),
        "context": event_data.get("context", {}),
    }

    if item:
        parsed["track"] = {
            "id": item.get("id"),
            "name": item.get("name"),
            "uri": item.get("uri"),
            "duration_ms": item.get("duration_ms"),
            "artists": [
                {"name": artist.get("name"), "id": artist.get("id")}
                for artist in item.get("artists", [])
            ],
            "album": {
                "name": item.get("album", {}).get("name"),
                "id": item.get("album", {}).get("id"),
            }
            if item.get("album")
            else None,
        }

    return parsed


def has_track_changed(old_playback: Optional[Dict], new_playback: Dict) -> bool:
    """
    Check if the currently playing track has changed.

    Args:
        old_playback: Previous playback state
        new_playback: Current playback state

    Returns:
        True if track changed, False otherwise
    """
    if not old_playback or not new_playback:
        return old_playback != new_playback

    old_track = old_playback.get("item", {}).get("id")
    new_track = new_playback.get("item", {}).get("id")

    return old_track != new_track


def has_playback_started(old_playback: Optional[Dict], new_playback: Dict) -> bool:
    """
    Check if playback has started (was paused/stopped, now playing).

    Args:
        old_playback: Previous playback state
        new_playback: Current playback state

    Returns:
        True if playback started, False otherwise
    """
    if not new_playback:
        return False

    was_playing = old_playback.get("is_playing", False) if old_playback else False
    is_playing = new_playback.get("is_playing", False)

    return not was_playing and is_playing


def has_playback_stopped(old_playback: Optional[Dict], new_playback: Dict) -> bool:
    """
    Check if playback has stopped (was playing, now paused/stopped).

    Args:
        old_playback: Previous playback state
        new_playback: Current playback state

    Returns:
        True if playback stopped, False otherwise
    """
    if not old_playback:
        return False

    was_playing = old_playback.get("is_playing", False)
    is_playing = new_playback.get("is_playing", False) if new_playback else False

    return was_playing and not is_playing
