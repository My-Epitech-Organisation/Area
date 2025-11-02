"""
Google Webhook (Push Notification) Receivers.

This module handles incoming push notifications from Google services:
- Gmail: History notifications when emails change
- Calendar: Event notifications when calendar events change
- YouTube: PubSubHubbub notifications for new videos

Google uses different notification mechanisms:
- Gmail/Calendar: Push API with channel_id verification
- YouTube: PubSubHubbub with hub.challenge verification
"""

import json
import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.http import HttpResponse

from .helpers.calendar_helper import list_upcoming_events
from .helpers.gmail_helper import get_history, get_message_details
from .helpers.youtube_helper import parse_atom_feed_entry
from .models import Area, GoogleWebhookWatch
from .tasks import create_execution_safe, execute_reaction_task

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def gmail_webhook(request):
    """
    Handle Gmail push notifications.

    GET: Domain verification (returns 200 OK)
    POST: Receive Gmail history notifications

    Gmail sends notifications when the mailbox changes (new emails, labels, etc.)
    We need to:
    1. Verify the channel_id matches an active watch
    2. Get the history_id from the notification
    3. Fetch actual changes using Gmail History API
    4. Trigger relevant Areas
    """
    if request.method == "GET":
        # Domain verification
        logger.info("Gmail webhook GET request (domain verification)")
        return HttpResponse("OK", status=200)

    try:
        # Parse notification headers
        channel_id = request.headers.get("X-Goog-Channel-ID")
        resource_state = request.headers.get("X-Goog-Resource-State")
        resource_id = request.headers.get("X-Goog-Resource-ID")

        if not channel_id:
            logger.warning("Gmail webhook: missing X-Goog-Channel-ID header")
            return HttpResponse("Missing channel ID", status=400)

        logger.info(
            f"Gmail webhook received: channel={channel_id}, "
            f"state={resource_state}, resource={resource_id}"
        )

        # Find the watch
        try:
            watch = GoogleWebhookWatch.objects.get(
                channel_id=channel_id, service=GoogleWebhookWatch.Service.GMAIL
            )
        except GoogleWebhookWatch.DoesNotExist:
            logger.warning(f"Gmail webhook: unknown channel_id {channel_id}")
            return HttpResponse("Unknown channel", status=404)

        # Record event
        watch.record_event()

        # Skip sync state (initial handshake)
        if resource_state == "sync":
            logger.info(f"Gmail webhook: sync state for channel {channel_id}")
            return HttpResponse("OK", status=200)

        # Parse notification body (contains historyId)
        try:
            body = json.loads(request.body.decode("utf-8"))
            history_id = body.get("historyId")
        except Exception as e:
            logger.error(f"Failed to parse Gmail notification body: {e}")
            history_id = None

        if not history_id:
            logger.warning("Gmail webhook: no historyId in notification")
            return HttpResponse("OK", status=200)

        # Fetch user's OAuth token
        from users.oauth.manager import OAuthManager

        access_token = OAuthManager.get_valid_token(watch.user, "google")

        if not access_token:
            logger.warning(
                f"Gmail webhook: no valid token for user {watch.user.username}"
            )
            return HttpResponse("No token", status=200)

        # Fetch history changes
        try:
            history = get_history(access_token, start_history_id=history_id)

            if not history:
                logger.debug(f"No Gmail history changes for user {watch.user.username}")
                return HttpResponse("OK", status=200)

            # Process history changes
            for history_item in history:
                messages_added = history_item.get("messagesAdded", [])

                for msg_info in messages_added:
                    message_id = msg_info.get("message", {}).get("id")
                    labels = msg_info.get("message", {}).get("labelIds", [])

                    # Only process INBOX messages
                    if "INBOX" not in labels:
                        continue

                    # Get message details
                    details = get_message_details(access_token, message_id)

                    # Find matching Areas
                    gmail_areas = Area.objects.filter(
                        owner=watch.user,
                        status=Area.Status.ACTIVE,
                        action__name__in=[
                            "gmail_new_email",
                            "gmail_new_from_sender",
                            "gmail_new_with_label",
                            "gmail_new_with_subject",
                        ],
                    ).select_related("action", "reaction")

                    for area in gmail_areas:
                        # Check if message matches action criteria
                        if not _gmail_message_matches_action(area, details):
                            continue

                        # Create execution
                        event_id = f"gmail_{message_id}"
                        trigger_data = {
                            "service": "gmail",
                            "action": area.action.name,
                            "message_id": message_id,
                            "subject": details["subject"],
                            "from": details["from"],
                            "to": details["to"],
                            "date": details["date"],
                            "snippet": details["snippet"],
                            "labels": details["labels"],
                        }

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Gmail webhook triggered area '{area.name}': "
                                f"Message from {details['from']}"
                            )
                            execute_reaction_task.delay(execution.pk)

        except Exception as e:
            logger.error(f"Error processing Gmail history: {e}", exc_info=True)

        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"Gmail webhook error: {e}", exc_info=True)
        return HttpResponse("Internal error", status=500)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def calendar_webhook(request):
    """
    Handle Google Calendar push notifications.

    GET: Domain verification
    POST: Receive Calendar change notifications

    Calendar sends notifications when events change (created, updated, deleted).
    """
    if request.method == "GET":
        # Domain verification
        logger.info("Calendar webhook GET request (domain verification)")
        return HttpResponse("OK", status=200)

    try:
        # Parse notification headers
        channel_id = request.headers.get("X-Goog-Channel-ID")
        resource_state = request.headers.get("X-Goog-Resource-State")
        resource_id = request.headers.get("X-Goog-Resource-ID")

        if not channel_id:
            logger.warning("Calendar webhook: missing X-Goog-Channel-ID header")
            return HttpResponse("Missing channel ID", status=400)

        logger.info(
            f"Calendar webhook received: channel={channel_id}, "
            f"state={resource_state}, resource={resource_id}"
        )

        # Find the watch
        try:
            watch = GoogleWebhookWatch.objects.get(
                channel_id=channel_id, service=GoogleWebhookWatch.Service.CALENDAR
            )
        except GoogleWebhookWatch.DoesNotExist:
            logger.warning(f"Calendar webhook: unknown channel_id {channel_id}")
            return HttpResponse("Unknown channel", status=404)

        # Record event
        watch.record_event()

        # Skip sync state
        if resource_state == "sync":
            logger.info(f"Calendar webhook: sync state for channel {channel_id}")
            return HttpResponse("OK", status=200)

        # Fetch user's OAuth token
        from users.oauth.manager import OAuthManager

        access_token = OAuthManager.get_valid_token(watch.user, "google")

        if not access_token:
            logger.warning(
                f"Calendar webhook: no valid token for user {watch.user.username}"
            )
            return HttpResponse("No token", status=200)

        # Fetch recent calendar events
        try:
            calendar_id = watch.resource_uri or "primary"
            events = list_upcoming_events(
                access_token, calendar_id=calendar_id, max_results=10
            )

            if not events:
                logger.debug(f"No calendar events for user {watch.user.username}")
                return HttpResponse("OK", status=200)

            # Find matching Areas
            calendar_areas = Area.objects.filter(
                owner=watch.user,
                status=Area.Status.ACTIVE,
                action__name__in=[
                    "calendar_new_event",
                    "calendar_event_starting_soon",
                ],
            ).select_related("action", "reaction")

            for area in calendar_areas:
                action_name = area.action.name

                if action_name == "calendar_new_event":
                    # Check for newly created events (created in last 5 minutes)
                    from datetime import timedelta

                    from django.utils import timezone

                    recent_threshold = timezone.now() - timedelta(minutes=5)

                    for event in events:
                        try:
                            from dateutil import parser

                            created_str = event.get("created", "")
                            if not created_str:
                                continue

                            created_dt = parser.isoparse(created_str)

                            if created_dt >= recent_threshold:
                                event_id = f"calendar_new_event_{event['id']}"

                                trigger_data = {
                                    "action": "calendar_new_event",
                                    "service": "google_calendar",
                                    "event_id": event["id"],
                                    "event_title": event.get("summary", ""),
                                    "event_description": event.get("description", ""),
                                    "event_location": event.get("location", ""),
                                    "start_time": event.get("start", {}).get(
                                        "dateTime", ""
                                    ),
                                    "end_time": event.get("end", {}).get(
                                        "dateTime", ""
                                    ),
                                    "attendees": [
                                        a.get("email", "")
                                        for a in event.get("attendees", [])
                                    ],
                                    "organizer": event.get("organizer", {}).get(
                                        "email", ""
                                    ),
                                    "created": created_str,
                                }

                                execution, created = create_execution_safe(
                                    area=area,
                                    external_event_id=event_id,
                                    trigger_data=trigger_data,
                                )

                                if created and execution:
                                    logger.info(
                                        f"Calendar webhook triggered area '{area.name}': "
                                        f"New event '{event.get('summary')}'"
                                    )
                                    execute_reaction_task.delay(execution.pk)

                        except Exception as e:
                            logger.error(
                                f"Error processing calendar event {event.get('id')}: {e}"
                            )

        except Exception as e:
            logger.error(f"Error processing calendar changes: {e}", exc_info=True)

        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"Calendar webhook error: {e}", exc_info=True)
        return HttpResponse("Internal error", status=500)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def youtube_webhook(request):
    """
    Handle YouTube PubSubHubbub notifications.

    GET: Hub verification (must respond with hub.challenge)
    POST: Receive new video notifications (Atom feed XML)
    """
    if request.method == "GET":
        # Hub verification
        challenge = request.GET.get("hub.challenge")
        if challenge:
            logger.info("YouTube webhook verification: responding with challenge")
            return HttpResponse(challenge, content_type="text/plain", status=200)
        return HttpResponse("OK", status=200)

    try:
        # Parse Atom feed XML
        body = request.body.decode("utf-8")
        video_data = parse_atom_feed_entry(body)

        if not video_data:
            logger.warning("YouTube webhook: failed to parse feed")
            return HttpResponse("Invalid feed", status=400)

        video_id = video_data["video_id"]
        channel_id = video_data["channel_id"]

        logger.info(f"YouTube webhook: new video {video_id} from channel {channel_id}")

        # Find users watching this channel
        youtube_areas = Area.objects.filter(
            status=Area.Status.ACTIVE,
            action__name="youtube_new_video",
            action_config__channel_id=channel_id,
        ).select_related("owner", "action", "reaction")

        for area in youtube_areas:
            event_id = f"youtube_new_video_{video_id}_{area.pk}"

            trigger_data = {
                "video_id": video_id,
                "video_title": video_data["title"],
                "video_description": video_data.get("description", ""),
                "channel_id": channel_id,
                "channel_name": video_data["channel_title"],
                "published_at": video_data["published_at"],
                "thumbnail_url": video_data.get("thumbnail_url", ""),
            }

            execution, created = create_execution_safe(
                area=area, external_event_id=event_id, trigger_data=trigger_data
            )

            if created and execution:
                logger.info(
                    f"YouTube webhook triggered area '{area.name}': "
                    f"New video '{video_data['title']}'"
                )
                execute_reaction_task.delay(execution.pk)

        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"YouTube webhook error: {e}", exc_info=True)
        return HttpResponse("Internal error", status=500)


def _gmail_message_matches_action(area, message_details):
    """
    Check if a Gmail message matches the Area's action criteria.

    Args:
        area: Area instance
        message_details: Dict with message details (from, subject, labels, etc.)

    Returns:
        bool: True if message matches action config
    """
    action_name = area.action.name
    action_config = area.action_config or {}

    # gmail_new_email: matches any email
    if action_name == "gmail_new_email":
        # Optional filters
        from_email = action_config.get("from_email")
        subject_contains = action_config.get("subject_contains")

        if from_email and from_email.lower() not in message_details["from"].lower():
            return False

        return not (
            subject_contains
            and subject_contains.lower() not in message_details["subject"].lower()
        )

    # gmail_new_from_sender: specific sender
    elif action_name == "gmail_new_from_sender":
        from_email = action_config.get("from_email", "").lower()
        return from_email in message_details["from"].lower()

    # gmail_new_with_label: specific label
    elif action_name == "gmail_new_with_label":
        required_label = action_config.get("label", "").lower()
        message_labels = [label.lower() for label in message_details.get("labels", [])]
        return required_label in message_labels

    # gmail_new_with_subject: subject contains text
    elif action_name == "gmail_new_with_subject":
        subject_contains = action_config.get("subject_contains", "").lower()
        return subject_contains in message_details["subject"].lower()

    return False
