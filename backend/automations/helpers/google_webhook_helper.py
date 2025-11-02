"""
Google Webhook (Push Notification) Helper Functions.

This module provides utilities for managing Google push notifications (watches)
for Gmail, Calendar, and YouTube services.

Key Concepts:
- Google uses "watches" instead of traditional webhooks
- Each watch has a unique channel_id (UUID) and resource_id (returned by Google)
- Watches expire after a period (7 days for Gmail, configurable for Calendar)
- Must renew watches before expiration

References:
- Gmail: https://developers.google.com/gmail/api/guides/push
- Calendar: https://developers.google.com/calendar/api/guides/push
- YouTube: https://developers.google.com/youtube/v3/guides/push_notifications
"""

import logging
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def create_gmail_watch(access_token, webhook_url, user_id=None):
    """
    Create a Gmail push notification watch.

    Args:
        access_token (str): Valid Google OAuth2 access token
        webhook_url (str): Full HTTPS URL to receive notifications
        user_id (str): Optional Gmail user ID (default: 'me')

    Returns:
        dict: Watch info with keys: channel_id, resource_id, expiration
        None: If watch creation failed

    Example:
        watch = create_gmail_watch(token, "https://areaction.app/api/webhooks/gmail/")
        # {'channel_id': 'uuid...', 'resource_id': 'abc123', 'expiration': datetime}
    """
    try:
        # Build Gmail API client
        service = build("gmail", "v1", credentials=None, static_discovery=False)
        service._http.credentials = type("Credentials", (), {"token": access_token})()

        # Generate unique channel ID
        channel_id = str(uuid.uuid4())

        # Create watch request
        request_body = {
            "labelIds": ["INBOX"],  # Watch INBOX only
            "topicName": f"projects/{settings.GOOGLE_CLOUD_PROJECT}/topics/gmail",
            "labelFilterAction": "include",
        }

        # For webhook-based notifications (not Pub/Sub)
        if not hasattr(settings, "GOOGLE_CLOUD_PROJECT"):
            request_body = {
                "labelIds": ["INBOX"],
            }

        # Gmail push notifications using Pub/Sub or direct webhook
        # Note: Gmail requires Pub/Sub for production, but we'll use direct webhook for simplicity
        watch_request = {
            "topicName": webhook_url,  # This should be a Pub/Sub topic in production
        }

        # Alternative: Use direct webhook (for testing, requires domain verification)
        user = user_id or "me"
        response = (
            service.users()
            .watch(userId=user, body={"labelIds": ["INBOX"], "topicName": webhook_url})
            .execute()
        )

        # Extract watch info
        history_id = response.get("historyId")
        expiration_ms = int(response.get("expiration", 0))

        # Gmail watch expires in ~7 days
        expiration = datetime.fromtimestamp(expiration_ms / 1000, tz=timezone.utc)

        logger.info(
            f"Gmail watch created successfully: channel={channel_id}, "
            f"expiration={expiration}"
        )

        return {
            "channel_id": channel_id,
            "resource_id": history_id,
            "expiration": expiration,
        }

    except HttpError as e:
        logger.error(f"Gmail watch creation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating Gmail watch: {e}", exc_info=True)
        return None


def stop_gmail_watch(access_token, channel_id, resource_id):
    """
    Stop (delete) a Gmail watch.

    Args:
        access_token (str): Valid Google OAuth2 access token
        channel_id (str): Channel ID of the watch to stop
        resource_id (str): Resource ID returned when watch was created

    Returns:
        bool: True if stopped successfully, False otherwise
    """
    try:
        service = build("gmail", "v1", credentials=None, static_discovery=False)
        service._http.credentials = type("Credentials", (), {"token": access_token})()

        service.users().stop(userId="me").execute()

        logger.info(f"Gmail watch stopped successfully: channel={channel_id}")
        return True

    except HttpError as e:
        logger.error(f"Failed to stop Gmail watch: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error stopping Gmail watch: {e}", exc_info=True)
        return False


def create_calendar_watch(access_token, calendar_id, webhook_url, expiration_hours=168):
    """
    Create a Google Calendar push notification watch.

    Args:
        access_token (str): Valid Google OAuth2 access token
        calendar_id (str): Calendar ID to watch (use 'primary' for main calendar)
        webhook_url (str): Full HTTPS URL to receive notifications
        expiration_hours (int): Watch duration in hours (max 604800 seconds = 1 week)

    Returns:
        dict: Watch info with keys: channel_id, resource_id, expiration
        None: If watch creation failed
    """
    try:
        service = build("calendar", "v3", credentials=None, static_discovery=False)
        service._http.credentials = type("Credentials", (), {"token": access_token})()

        # Generate unique channel ID
        channel_id = str(uuid.uuid4())

        # Calculate expiration (max 1 week for Calendar)
        expiration_seconds = min(expiration_hours * 3600, 604800)
        expiration = timezone.now() + timedelta(seconds=expiration_seconds)

        # Create watch request body
        request_body = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "expiration": int(expiration.timestamp() * 1000),  # Milliseconds
        }

        # Create the watch
        response = (
            service.events()
            .watch(calendarId=calendar_id, body=request_body)
            .execute()
        )

        # Extract watch info
        resource_id = response.get("resourceId")
        resource_uri = response.get("resourceUri")

        logger.info(
            f"Calendar watch created: channel={channel_id}, "
            f"resource={resource_id}, expiration={expiration}"
        )

        return {
            "channel_id": channel_id,
            "resource_id": resource_id,
            "resource_uri": resource_uri,
            "expiration": expiration,
        }

    except HttpError as e:
        logger.error(f"Calendar watch creation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating Calendar watch: {e}", exc_info=True)
        return None


def stop_calendar_watch(access_token, channel_id, resource_id):
    """
    Stop (delete) a Google Calendar watch.

    Args:
        access_token (str): Valid Google OAuth2 access token
        channel_id (str): Channel ID of the watch to stop
        resource_id (str): Resource ID returned when watch was created

    Returns:
        bool: True if stopped successfully, False otherwise
    """
    try:
        service = build("calendar", "v3", credentials=None, static_discovery=False)
        service._http.credentials = type("Credentials", (), {"token": access_token})()

        request_body = {"id": channel_id, "resourceId": resource_id}

        service.channels().stop(body=request_body).execute()

        logger.info(f"Calendar watch stopped: channel={channel_id}")
        return True

    except HttpError as e:
        logger.error(f"Failed to stop Calendar watch: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error stopping Calendar watch: {e}", exc_info=True)
        return False


def create_youtube_watch(channel_id, webhook_url):
    """
    Subscribe to YouTube PubSubHubbub notifications.

    NOTE: YouTube uses a different system (PubSubHubbub) rather than the
    watch API used by Gmail/Calendar.

    Args:
        channel_id (str): YouTube channel ID to watch
        webhook_url (str): Full HTTPS URL to receive notifications

    Returns:
        dict: Subscription info with keys: channel_id, expiration (10 days)
        None: If subscription failed
    """
    import requests

    try:
        # PubSubHubbub hub URL
        hub_url = "https://pubsubhubbub.appspot.com/subscribe"

        # Topic URL (channel feed)
        topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"

        # Subscribe request
        data = {
            "hub.mode": "subscribe",
            "hub.topic": topic_url,
            "hub.callback": webhook_url,
            "hub.verify": "async",  # Async verification
            "hub.lease_seconds": 864000,  # 10 days
        }

        response = requests.post(hub_url, data=data, timeout=10)

        if response.status_code == 202:
            # Subscription accepted (will be verified asynchronously)
            expiration = timezone.now() + timedelta(days=10)

            logger.info(
                f"YouTube PubSubHubbub subscription created for channel {channel_id}"
            )

            return {
                "channel_id": channel_id,
                "resource_id": topic_url,
                "expiration": expiration,
            }
        else:
            logger.error(
                f"YouTube subscription failed: {response.status_code} - {response.text}"
            )
            return None

    except Exception as e:
        logger.error(f"Unexpected error creating YouTube watch: {e}", exc_info=True)
        return None


def renew_youtube_watch(channel_id, webhook_url):
    """Renew YouTube PubSubHubbub subscription (same as create)."""
    return create_youtube_watch(channel_id, webhook_url)
