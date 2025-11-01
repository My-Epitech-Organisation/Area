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
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Area, Service
from .tasks import create_execution_safe, execute_reaction, get_active_areas
from .webhook_constants import WEBHOOK_EVENT_TO_ACTION

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


def validate_notion_signature(payload_body: bytes, headers: dict, secret: str) -> bool:
    """
    Validate Notion webhook signature using HMAC-SHA256.

    Notion sends signature in X-Notion-Signature header.

    Args:
        payload_body: Raw request body as bytes
        headers: Request headers dict
        secret: Webhook secret configured in Notion

    Returns:
        True if signature is valid, False otherwise
    """
    signature_header = headers.get("X-Notion-Signature")

    if not signature_header:
        logger.warning("Notion webhook: No signature header provided")
        return False

    # Notion signature is already in hex format (not prefixed with algorithm)
    expected_signature = signature_header

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
    elif service_name == "gmail":
        return True
    elif service_name == "notion":
        return validate_notion_signature(payload_body, headers, secret)
    # Unknown service, reject validation
    logger.warning(f"Webhook signature validation not supported for: {service_name}")
    return False


def extract_event_id(
    service_name: str, event_data: dict, headers: dict = None
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

    elif service_name == "gmail":
        # Gmail Pub/Sub provides message ID
        message_id = event_data.get("message", {}).get("messageId")
        if message_id:
            return f"gmail_message_{message_id}"

    elif service_name == "notion":
        # Notion provides timestamp and data in webhook
        timestamp = event_data.get("timestamp")
        data = event_data.get("data", {})

        # Use object ID and timestamp for uniqueness
        object_id = data.get("id")
        if object_id and timestamp:
            return f"notion_{object_id}_{timestamp}"

        # Fallback
        if object_id:
            return f"notion_{object_id}"

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
        service_name: Name of the service (github, gmail)
        event_type: Type of event (push, pull_request, email_received, etc.)
        event_data: Full webhook payload

    Returns:
        List of Area objects that match this event
    """
    # Use centralized event-to-action mapping
    action_names = []
    if service_name in WEBHOOK_EVENT_TO_ACTION:
        action_map = WEBHOOK_EVENT_TO_ACTION[service_name]
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



def process_webhook_event(
    service_name: str,
    event_type: str,
    event_data: dict,
    headers: dict,
) -> dict[str, Any]:
    """
    Process a validated webhook event.

    Steps:
    1. Extract unique event ID
    2. Match event to active Areas
    3. Create executions for matched Areas
    4. Queue reactions

    Args:
        service_name: Name of the service
        event_type: Type of event
        event_data: Parsed webhook payload
        headers: Request headers

    Returns:
        Processing result with statistics
    """
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
                execute_reaction.delay(execution.pk)
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
    elif service == "gmail":
        event_type = event_data.get("eventType", "message")
    elif service == "notion":
        # Notion webhooks contain type information in the data
        data = event_data.get("data", {})
        object_type = data.get("object", "unknown")
        event_type = object_type  # "page" or "database"
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

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(
            f"Error processing webhook {service}/{event_type}: {e}", exc_info=True
        )
        return Response(
            {"error": "Internal server error processing webhook"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
