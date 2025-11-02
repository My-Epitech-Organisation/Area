##
## EPITECH PROJECT, 2025
## Area
## File description:
## calendar_helper
##

"""Google Calendar API helper functions for actions and reactions."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def get_calendar_service(access_token: str):
    """
    Build Google Calendar API service from access token.

    Args:
        access_token: Valid Google OAuth2 access token

    Returns:
        Calendar API service resource
    """
    creds = Credentials(token=access_token)
    return build("calendar", "v3", credentials=creds)


def list_upcoming_events(
    access_token: str,
    max_results: int = 10,
    time_min: Optional[str] = None,
    calendar_id: str = "primary",
) -> List[Dict]:
    """
    List upcoming calendar events.

    Args:
        access_token: Valid Google OAuth token
        max_results: Max events to return (default: 10)
        time_min: RFC3339 timestamp for earliest event (default: now)
        calendar_id: Calendar ID to query (default: "primary")

    Returns:
        List of event dicts with id, summary, start, end

    Raises:
        HttpError: If Calendar API request fails
    """
    try:
        service = get_calendar_service(access_token)

        if not time_min:
            time_min = datetime.now(timezone.utc).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        logger.info(f"Found {len(events)} upcoming calendar events")
        return events

    except HttpError as e:
        logger.error(f"Calendar list_upcoming_events failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_upcoming_events: {e}")
        raise


def get_event(access_token: str, event_id: str) -> Dict:
    """
    Get details of a specific calendar event.

    Args:
        access_token: Valid Google OAuth token
        event_id: Calendar event ID

    Returns:
        Dict with event details

    Raises:
        HttpError: If Calendar API request fails
    """
    try:
        service = get_calendar_service(access_token)
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        logger.info(f"Retrieved calendar event: {event.get('summary', 'Untitled')}")
        return event

    except HttpError as e:
        logger.error(f"Calendar get_event failed for {event_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_event: {e}")
        raise


def create_event(
    access_token: str,
    summary: str,
    start: str,
    end: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
) -> Dict:
    """
    Create a new calendar event.

    Args:
        access_token: Valid Google OAuth token
        summary: Event title
        start: RFC3339 timestamp for event start (e.g., "2025-10-14T10:00:00Z")
        end: RFC3339 timestamp for event end
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee emails (optional)

    Returns:
        Dict with created event details including id and link

    Raises:
        HttpError: If Calendar API request fails
        ValueError: If required parameters are missing
    """
    if not summary or not start or not end:
        raise ValueError("summary, start, and end are required")

    try:
        service = get_calendar_service(access_token)

        event_body = {
            "summary": summary,
            "description": description,
            "location": location,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }

        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        result = (
            service.events().insert(calendarId="primary", body=event_body).execute()
        )

        logger.info(
            f"Created calendar event: {result['summary']} ({result.get('htmlLink')})"
        )
        return result

    except HttpError as e:
        logger.error(f"Calendar create_event failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_event: {e}")
        raise


def update_event(
    access_token: str,
    event_id: str,
    summary: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict:
    """
    Update an existing calendar event.

    Args:
        access_token: Valid Google OAuth token
        event_id: Calendar event ID to update
        summary: New event title (optional)
        start: New RFC3339 timestamp for start (optional)
        end: New RFC3339 timestamp for end (optional)
        description: New event description (optional)

    Returns:
        Dict with updated event details

    Raises:
        HttpError: If Calendar API request fails
    """
    try:
        service = get_calendar_service(access_token)

        # Get existing event
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        # Update fields if provided
        if summary:
            event["summary"] = summary
        if description is not None:
            event["description"] = description
        if start:
            event["start"] = {"dateTime": start, "timeZone": "UTC"}
        if end:
            event["end"] = {"dateTime": end, "timeZone": "UTC"}

        # Update event
        result = (
            service.events()
            .update(calendarId="primary", eventId=event_id, body=event)
            .execute()
        )

        logger.info(f"Updated calendar event: {result['summary']}")
        return result

    except HttpError as e:
        logger.error(f"Calendar update_event failed for {event_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_event: {e}")
        raise


def delete_event(access_token: str, event_id: str) -> bool:
    """
    Delete a calendar event.

    Args:
        access_token: Valid Google OAuth token
        event_id: Calendar event ID to delete

    Returns:
        bool: True if deleted successfully

    Raises:
        HttpError: If Calendar API request fails
    """
    try:
        service = get_calendar_service(access_token)
        service.events().delete(calendarId="primary", eventId=event_id).execute()

        logger.info(f"Deleted calendar event: {event_id}")
        return True

    except HttpError as e:
        logger.error(f"Calendar delete_event failed for {event_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_event: {e}")
        raise
