##
## EPITECH PROJECT, 2025
## Area
## File description:
## webhooks
##

"""
Webhook receiver for external service events.

This module handles incoming webhook events from external services like:
- GitHub (push, pull_request, issues, etc.)
- Gmail (via Pub/Sub notifications)
- Other services with webhook support

Features:
- HMAC-SHA256 signature verification
- Service-specific event parsing
- Automatic Area matching and execution creation
- Idempotency via external_event_id
"""

import hashlib
import hmac
import json
import logging
from typing import Any, Optional

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Area, Service
from .tasks import create_execution_safe, get_active_areas

logger = logging.getLogger(__name__)


def validate_github_signature(
    payload_body: bytes, signature_header: str, secret: str
) -> bool:
    """
    Validate GitHub webhook signature using HMAC-SHA256.

    GitHub sends signature in format: "sha256=<signature>"

    Args:
        payload_body: Raw request body as bytes
        signature_header: Value of X-Hub-Signature-256 header
        secret: Webhook secret configured in GitHub

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature_header:
        logger.warning("GitHub webhook: No signature header provided")
        return False

    if not signature_header.startswith("sha256="):
        logger.warning(f"GitHub webhook: Invalid signature format: {signature_header}")
        return False

    # Extract signature from header
    expected_signature = signature_header.split("=", 1)[1]

    # Compute HMAC-SHA256
    computed_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_signature, expected_signature)


def validate_twitch_signature(payload_body: bytes, headers: dict, secret: str) -> bool:
    """
    Validate Twitch EventSub webhook signature using HMAC-SHA256.

    Twitch sends signature in headers:
    - Twitch-Eventsub-Message-Id
    - Twitch-Eventsub-Message-Timestamp
    - Twitch-Eventsub-Message-Signature (format: "sha256=<signature>")

    Args:
        payload_body: Raw request body as bytes
        headers: Request headers dict
        secret: Webhook secret configured in Twitch EventSub

    Returns:
        True if signature is valid, False otherwise
    """
    message_id = headers.get("Twitch-Eventsub-Message-Id")
    message_timestamp = headers.get("Twitch-Eventsub-Message-Timestamp")
    signature_header = headers.get("Twitch-Eventsub-Message-Signature")

    if not all([message_id, message_timestamp, signature_header]):
        logger.warning("Twitch webhook: Missing required headers")
        return False

    if not signature_header.startswith("sha256="):
        logger.warning(f"Twitch webhook: Invalid signature format: {signature_header}")
        return False

    # Extract signature from header
    expected_signature = signature_header.split("=", 1)[1]

    # Construct message to verify
    # Format: <message_id><message_timestamp><request_body>
    message = (
        message_id.encode("utf-8") + message_timestamp.encode("utf-8") + payload_body
    )

    # Compute HMAC-SHA256
    computed_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=message,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_signature, expected_signature)


def validate_slack_signature(payload_body: bytes, headers: dict, secret: str) -> bool:
    """
    Validate Slack Events API webhook signature.

    Slack sends signature in headers:
    - X-Slack-Request-Timestamp
    - X-Slack-Signature (format: "v0=<signature>")

    Args:
        payload_body: Raw request body as bytes
        headers: Request headers dict
        secret: Slack signing secret

    Returns:
        True if signature is valid, False otherwise
    """
    timestamp = headers.get("X-Slack-Request-Timestamp")
    signature_header = headers.get("X-Slack-Signature")

    if not all([timestamp, signature_header]):
        logger.warning("Slack webhook: Missing required headers")
        return False

    if not signature_header.startswith("v0="):
        logger.warning(f"Slack webhook: Invalid signature format: {signature_header}")
        return False

    # Check timestamp to prevent replay attacks (within 5 minutes)
    try:
        request_timestamp = int(timestamp)
        current_timestamp = int(timezone.now().timestamp())
        if abs(current_timestamp - request_timestamp) > 60 * 5:
            logger.warning("Slack webhook: Request timestamp too old")
            return False
    except (ValueError, TypeError):
        logger.warning(f"Slack webhook: Invalid timestamp: {timestamp}")
        return False

    # Extract signature from header
    expected_signature = signature_header.split("=", 1)[1]

    # Construct signing basestring
    # Format: v0:<timestamp>:<body>
    sig_basestring = f"v0:{timestamp}:".encode("utf-8") + payload_body

    # Compute HMAC-SHA256
    computed_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=sig_basestring,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_signature, expected_signature)


def validate_webhook_signature(
    service_name: str, payload_body: bytes, headers: dict, secret: str
) -> bool:
    """
    Validate webhook signature for any service.

    Dispatches to service-specific validation functions.

    Args:
        service_name: Name of the service (github, gmail, etc.)
        payload_body: Raw request body as bytes
        headers: Request headers dict
        secret: Webhook secret for the service

    Returns:
        True if signature is valid, False otherwise
    """
    if service_name == "github":
        signature_header = headers.get("X-Hub-Signature-256", "")
        return validate_github_signature(payload_body, signature_header, secret)
    elif service_name == "twitch":
        return validate_twitch_signature(payload_body, headers, secret)
    elif service_name == "slack":
        return validate_slack_signature(payload_body, headers, secret)
    elif service_name == "gmail":
        return True
    # Unknown service, reject validation
    return False


def extract_event_id(
    service_name: str, event_data: dict, headers: Optional[dict] = None
) -> Optional[str]:
    """
    Extract unique event ID from webhook payload.

    Args:
        service_name: Name of the service
        event_data: Parsed webhook payload
        headers: Request headers dict

    Returns:
        Unique event ID or None
    """
    if service_name == "github":
        # GitHub provides unique delivery ID
        delivery_id = event_data.get("delivery", event_data.get("hook_id"))
        if delivery_id:
            return f"github_delivery_{delivery_id}"

        # Fallback: use commit SHA or issue/PR number
        if "commits" in event_data and event_data["commits"]:
            return f"github_push_{event_data['commits'][0]['id']}"
        if "pull_request" in event_data:
            return f"github_pr_{event_data['pull_request']['id']}"
        if "issue" in event_data:
            return f"github_issue_{event_data['issue']['id']}"

    elif service_name == "twitch":
        # Twitch EventSub provides message ID in headers
        if headers:
            message_id = headers.get("Twitch-Eventsub-Message-Id")
            if message_id:
                return f"twitch_eventsub_{message_id}"

        # Fallback: use event data
        subscription = event_data.get("subscription", {})
        event = event_data.get("event", {})

        if subscription.get("id") and event:
            return f"twitch_{subscription['type']}_{subscription['id']}"

    elif service_name == "slack":
        # Slack provides event ID in payload
        event_id = event_data.get("event_id")
        if event_id:
            return f"slack_event_{event_id}"

        # For message events, use channel + timestamp
        event = event_data.get("event", {})
        if event.get("channel") and event.get("ts"):
            return f"slack_{event['channel']}_{event['ts']}"

    elif service_name == "gmail":
        # Gmail Pub/Sub provides message ID
        message_id = event_data.get("message", {}).get("messageId")
        if message_id:
            return f"gmail_message_{message_id}"

    # Fallback: generate ID from timestamp and hash
    timestamp = timezone.now().isoformat()
    payload_hash = hashlib.sha256(json.dumps(event_data).encode()).hexdigest()[:16]
    return f"{service_name}_{timestamp}_{payload_hash}"


def match_webhook_to_areas(
    service_name: str, event_type: str, event_data: dict
) -> list[Area]:
    """
    Find all active Areas that should trigger for this webhook event.

    Args:
        service_name: Name of the service (github, gmail, twitch)
        event_type: Type of event (push, pull_request, email_received, etc.)
        event_data: Full webhook payload

    Returns:
        List of Area objects that match this event
    """
    # Map event types to action names
    action_name_map = {
        "github": {
            "push": "github_push",
            "pull_request": "github_new_pr",
            "issues": "github_new_issue",
            "issue_comment": "github_issue_comment",
            "star": "github_star",
        },
        "gmail": {
            "message": "gmail_new_email",
            "email_received": "gmail_new_email",
        },
        "twitch": {
            "stream.online": "twitch_stream_online",
            "stream.offline": "twitch_stream_offline",
            "channel.follow": "twitch_new_follower",
            "channel.subscribe": "twitch_new_subscriber",
            "channel.update": "twitch_channel_update",
        },
        "slack": {
            "message": "slack_new_message",
            "app_mention": "slack_user_mention",
            "member_joined_channel": "slack_channel_join",
        },
    }

    action_names = []
    if service_name in action_name_map:
        action_map = action_name_map[service_name]
        if event_type in action_map:
            action_names.append(action_map[event_type])

    if not action_names:
        logger.debug(f"No action mapping for {service_name}/{event_type}")
        return []

    # Get all active areas for these actions
    areas = get_active_areas(action_names)

    # TODO: Add filtering based on action_config
    # e.g., only trigger for specific repositories, branches, labels, etc.

    return list(areas)


def process_github_app_installation(event_type: str, action: str, event_data: dict) -> dict:
    """
    Process GitHub App installation events.

    Events handled:
    - installation.created → User installs the app
    - installation.deleted → User uninstalls the app
    - installation_repositories.added → Repos added to installation
    - installation_repositories.removed → Repos removed from installation

    Args:
        event_type: "installation" or "installation_repositories"
        action: "created", "deleted", "added", "removed"
        event_data: GitHub webhook payload

    Returns:
        Processing result
    """
    from .models import GitHubAppInstallation
    from users.models import User

    installation = event_data.get("installation", {})
    installation_id = installation.get("id")
    account = installation.get("account", {})
    account_login = account.get("login")
    account_type = account.get("type")  # "User" or "Organization"

    if not installation_id:
        logger.error("GitHub App event missing installation.id")
        return {"status": "error", "message": "Missing installation ID"}

    logger.info(
        f"Processing GitHub App {event_type}.{action} "
        f"for installation {installation_id} ({account_login})"
    )

    if event_type == "installation":
        if action == "created":
            # User installed the app
            repositories = [
                repo["full_name"]
                for repo in event_data.get("repositories", [])
            ]

            # Try to find user by GitHub username
            # Note: This requires the user to have connected via OAuth first
            user = User.objects.filter(
                tokens__service__name="github",
                tokens__external_user_id=account.get("id")
            ).first()

            if not user:
                # Create installation without user link
                # User will link it when they log in via OAuth
                logger.warning(
                    f"No AREA user found for GitHub account {account_login}. "
                    "Installation will be linked when user logs in."
                )

            GitHubAppInstallation.objects.update_or_create(
                installation_id=installation_id,
                defaults={
                    "user": user,
                    "account_login": account_login,
                    "account_type": account_type,
                    "repositories": repositories,
                    "is_active": True,
                }
            )

            logger.info(
                f"GitHub App installed: {installation_id} "
                f"with {len(repositories)} repositories"
            )

            return {
                "status": "success",
                "action": "created",
                "installation_id": installation_id,
                "repositories_count": len(repositories)
            }

        elif action == "deleted":
            # User uninstalled the app
            installation_obj = GitHubAppInstallation.objects.filter(
                installation_id=installation_id
            ).first()

            if installation_obj:
                installation_obj.deactivate()
                logger.info(f"GitHub App uninstalled: {installation_id}")

            return {
                "status": "success",
                "action": "deleted",
                "installation_id": installation_id
            }

    elif event_type == "installation_repositories":
        installation_obj = GitHubAppInstallation.objects.filter(
            installation_id=installation_id
        ).first()

        if not installation_obj:
            logger.warning(
                f"Installation {installation_id} not found for repositories event"
            )
            return {
                "status": "error",
                "message": "Installation not found"
            }

        if action == "added":
            added_repos = [
                repo["full_name"]
                for repo in event_data.get("repositories_added", [])
            ]
            installation_obj.add_repositories(added_repos)
            logger.info(
                f"Added {len(added_repos)} repositories to "
                f"installation {installation_id}"
            )

            return {
                "status": "success",
                "action": "added",
                "installation_id": installation_id,
                "repositories_added": len(added_repos)
            }

        elif action == "removed":
            removed_repos = [
                repo["full_name"]
                for repo in event_data.get("repositories_removed", [])
            ]
            installation_obj.remove_repositories(removed_repos)
            logger.info(
                f"Removed {len(removed_repos)} repositories from "
                f"installation {installation_id}"
            )

            return {
                "status": "success",
                "action": "removed",
                "installation_id": installation_id,
                "repositories_removed": len(removed_repos)
            }

    return {
        "status": "ignored",
        "message": f"Unsupported event: {event_type}.{action}"
    }


def process_webhook_event(
    service_name: str,
    event_type: str,
    event_data: dict,
    headers: dict,
) -> dict[str, Any]:
    """
    Process a validated webhook event.

    Steps:
    1. Handle service-specific challenges/verification
    2. Extract unique event ID
    3. Match event to active Areas
    4. Create executions for matched Areas
    5. Queue reactions

    Args:
        service_name: Name of the service
        event_type: Type of event
        event_data: Parsed webhook payload
        headers: Request headers

    Returns:
        Processing result with statistics
    """
    # Handle Slack URL verification challenge
    if service_name == "slack" and event_type == "url_verification":
        challenge = event_data.get("challenge")
        logger.info("Slack URL verification challenge received")
        return {
            "status": "challenge",
            "challenge": challenge,
        }

    # Handle Twitch EventSub challenge verification
    if service_name == "twitch":
        message_type = headers.get("Twitch-Eventsub-Message-Type")

        # Challenge verification (webhook subscription confirmation)
        if message_type == "webhook_callback_verification":
            challenge = event_data.get("challenge")
            logger.info("Twitch EventSub challenge received")
            return {
                "status": "challenge",
                "challenge": challenge,
            }

        # Revocation notification (subscription cancelled)
        elif message_type == "revocation":
            subscription = event_data.get("subscription", {})
            logger.warning(f"Twitch EventSub revoked: {subscription.get('type')}")
            return {
                "status": "revoked",
                "subscription_type": subscription.get("type"),
            }

        # Extract actual event type from Twitch payload
        if "subscription" in event_data:
            event_type = event_data["subscription"]["type"]

    # Extract Slack event type from nested event object
    if service_name == "slack" and "event" in event_data:
        slack_event = event_data["event"]
        event_type = slack_event.get("type", event_type)

    # Extract event ID for idempotency
    external_event_id = extract_event_id(service_name, event_data, headers)
    if not external_event_id:
        logger.error(f"Could not extract event ID for {service_name}/{event_type}")
        return {
            "status": "error",
            "message": "Could not extract event ID",
        }

    # Match to areas
    matched_areas = match_webhook_to_areas(service_name, event_type, event_data)

    if not matched_areas:
        logger.info(
            f"No areas matched for {service_name}/{event_type} "
            f"(event: {external_event_id})"
        )
        return {
            "status": "success",
            "message": "No areas matched",
            "event_id": external_event_id,
            "matched_areas": 0,
            "executions_created": 0,
        }

    # Create executions for matched areas
    executions_created = 0
    executions_skipped = 0

    for area in matched_areas:
        try:
            # Prepare trigger data
            trigger_data = {
                "service": service_name,
                "event_type": event_type,
                "timestamp": timezone.now().isoformat(),
                "event_data": event_data,
                "headers": {
                    k: v
                    for k, v in headers.items()
                    if k.lower() not in ["authorization", "x-hub-signature-256"]
                },
            }

            # Create execution with idempotency
            execution, created = create_execution_safe(
                area=area,
                external_event_id=f"{external_event_id}_area_{area.pk}",
                trigger_data=trigger_data,
            )

            if created and execution:
                # Queue reaction execution
                from .tasks import execute_reaction_task

                execute_reaction_task.delay(execution.pk)
                executions_created += 1
                logger.info(
                    f"Webhook {service_name}/{event_type} triggered area '{area.name}' "
                    f"(execution #{execution.pk})"
                )
            else:
                executions_skipped += 1

        except Exception as e:
            logger.error(
                f"Error creating execution for area {area.pk} "
                f"from webhook {service_name}/{event_type}: {e}",
                exc_info=True,
            )

    return {
        "status": "success",
        "event_id": external_event_id,
        "matched_areas": len(matched_areas),
        "executions_created": executions_created,
        "executions_skipped": executions_skipped,
    }


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    request=None,  # No specific request serializer
    responses={200: None},  # Generic response
)
def webhook_receiver(request: Request, service: str) -> Response:
    """
    Universal webhook receiver endpoint.

    Receives webhooks from external services, validates signatures,
    and triggers matching Areas.

    URL: /webhooks/<service>/
    Method: POST

    Headers (service-specific):
    - GitHub: X-Hub-Signature-256, X-GitHub-Event, X-GitHub-Delivery
    - Gmail: Authorization (Bearer token)

    Args:
        request: DRF Request object
        service: Service name (github, gmail, etc.)

    Returns:
        JSON response with processing results
    """
    logger.info(f"Received webhook for service: {service}")

    # Check if service exists
    try:
        Service.objects.get(name=service, status=Service.Status.ACTIVE)
    except Service.DoesNotExist:
        logger.warning(f"Webhook received for unknown/inactive service: {service}")
        return Response(
            {"error": f"Service '{service}' not found or inactive"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Get raw body for signature verification
    try:
        raw_body = request.body
    except Exception as e:
        logger.error(f"Could not read request body: {e}")
        return Response(
            {"error": "Could not read request body"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Parse JSON payload
    try:
        if isinstance(request.data, dict):
            event_data = request.data
        else:
            event_data = json.loads(raw_body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Invalid JSON payload: {e}")
        return Response(
            {"error": "Invalid JSON payload"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get webhook secret from settings
    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
    webhook_secret = webhook_secrets.get(service)

    if not webhook_secret:
        logger.error(f"No webhook secret configured for service: {service}")
        return Response(
            {"error": "Webhook secret not configured"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Validate signature
    headers_dict = dict(request.headers.items())

    if not validate_webhook_signature(service, raw_body, headers_dict, webhook_secret):
        logger.warning(f"Invalid webhook signature for service: {service}")
        return Response(
            {"error": "Invalid webhook signature"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Extract event type
    if service == "github":
        event_type = request.headers.get("X-GitHub-Event", "unknown")

        # Handle GitHub App installation events
        if event_type in ["installation", "installation_repositories"]:
            action = event_data.get("action", "unknown")
            logger.info(
                f"Processing GitHub App {event_type}.{action} event"
            )

            try:
                result = process_github_app_installation(
                    event_type=event_type,
                    action=action,
                    event_data=event_data
                )
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(
                    f"Error processing GitHub App installation: {e}",
                    exc_info=True
                )
                return Response(
                    {"error": "Internal server error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    elif service == "twitch":
        # Twitch sends message type in header
        event_type = request.headers.get("Twitch-Eventsub-Message-Type", "notification")
    elif service == "slack":
        # Slack sends event type in payload
        event_type = event_data.get("type", "event_callback")
        # For event_callback, also get nested event type
        if event_type == "event_callback" and "event" in event_data:
            slack_event_type = event_data["event"].get("type", "unknown")
            logger.info(f"Slack event_callback with nested event: {slack_event_type}")
    elif service == "gmail":
        event_type = event_data.get("eventType", "message")
    else:
        event_type = event_data.get("event_type", "unknown")

    logger.info(f"Webhook {service}/{event_type} validated, processing...")

    # Process the webhook
    try:
        result = process_webhook_event(
            service_name=service,
            event_type=event_type,
            event_data=event_data,
            headers=headers_dict,
        )

        # Handle challenge responses (Twitch and Slack)
        if result.get("status") == "challenge" and "challenge" in result:
            # Twitch requires plain text response with just the challenge string
            if service == "twitch":
                return HttpResponse(
                    result["challenge"],
                    content_type="text/plain",
                    status=200
                )
            # Slack expects JSON response
            return Response(
                {"challenge": result["challenge"]},
                status=status.HTTP_200_OK
            )

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(
            f"Error processing webhook {service}/{event_type}: {e}", exc_info=True
        )
        return Response(
            {"error": "Internal server error processing webhook"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
