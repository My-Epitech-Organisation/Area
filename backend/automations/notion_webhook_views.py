##
## EPITECH PROJECT, 2025
## Area
## File description:
## notion_webhook_views
##

"""
API endpoints for Notion webhook management.

These views handle:
- Checking webhook status for a user
- Creating new webhook subscriptions via Notion API
- Deleting webhook subscriptions
- Listing active webhooks
"""

import logging

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.conf import settings

from users.oauth.manager import OAuthManager

from .models import NotionWebhookSubscription

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notion_webhook_status(request):
    """
    Check if user has Notion webhooks configured.

    Returns:
        {
            "webhooks_configured": bool,
            "subscriptions": [
                {
                    "webhook_id": str,
                    "workspace_id": str,
                    "page_id": str,
                    "database_id": str,
                    "event_types": list,
                    "status": str,
                    "created_at": datetime,
                    "event_count": int
                }
            ]
        }
    """
    subscriptions = NotionWebhookSubscription.objects.filter(
        user=request.user, status=NotionWebhookSubscription.Status.ACTIVE
    )

    return Response(
        {
            "webhooks_configured": subscriptions.exists(),
            "subscriptions": [
                {
                    "webhook_id": sub.webhook_id,
                    "workspace_id": sub.workspace_id,
                    "page_id": sub.page_id,
                    "database_id": sub.database_id,
                    "event_types": sub.event_types,
                    "status": sub.status,
                    "created_at": sub.created_at.isoformat(),
                    "event_count": sub.event_count,
                    "last_event_at": (
                        sub.last_event_at.isoformat() if sub.last_event_at else None
                    ),
                }
                for sub in subscriptions
            ],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def notion_webhook_create(request):
    """
    Create a Notion webhook subscription.

    Request body:
        {
            "page_id": str (optional),
            "database_id": str (optional),
            "event_types": ["page.updated", "database.updated"] (optional)
        }

    At least one of page_id or database_id must be provided.

    Returns:
        {
            "success": bool,
            "webhook_id": str,
            "message": str
        }
    """
    page_id = request.data.get("page_id", "").strip()
    database_id = request.data.get("database_id", "").strip()
    event_types = request.data.get("event_types", [])

    # Validation
    if not page_id and not database_id:
        return Response(
            {"error": "Either page_id or database_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Default event types if not provided
    if not event_types:
        if page_id:
            event_types = ["page.updated"]
        else:
            event_types = ["database.updated"]

    # Get Notion access token
    access_token = OAuthManager.get_valid_token(request.user, "notion")
    if not access_token:
        return Response(
            {"error": "No valid Notion token. Please reconnect Notion."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Construct webhook URL
    backend_url = getattr(settings, "BACKEND_URL", "http://localhost:8080")
    webhook_url = f"{backend_url}/api/webhooks/notion/"

    logger.info(
        f"Creating Notion webhook for user {request.user.username}: "
        f"page_id={page_id}, database_id={database_id}, events={event_types}"
    )

    # Create webhook via Notion API
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    payload = {
        "url": webhook_url,
        "event_types": event_types,
    }

    if page_id:
        payload["page_id"] = page_id
    if database_id:
        payload["database_id"] = database_id

    try:
        response = requests.post(
            "https://api.notion.com/v1/webhooks",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 201:
            webhook_data = response.json()
            webhook_id = webhook_data.get("id")
            workspace_id = webhook_data.get("workspace_id", "")

            # Save subscription in database
            subscription = NotionWebhookSubscription.objects.create(
                user=request.user,
                webhook_id=webhook_id,
                workspace_id=workspace_id,
                page_id=page_id,
                database_id=database_id,
                event_types=event_types,
                status=NotionWebhookSubscription.Status.ACTIVE,
            )

            logger.info(
                f"Created Notion webhook {webhook_id} for user {request.user.username}"
            )

            return Response(
                {
                    "success": True,
                    "webhook_id": webhook_id,
                    "workspace_id": workspace_id,
                    "message": "Webhook created successfully. Real-time notifications enabled!",
                }
            )
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get("message", "Unknown error")
            logger.error(
                f"Notion webhook creation failed: {response.status_code} - {error_msg}"
            )
            return Response(
                {"error": "Failed to create webhook", "details": error_msg},
                status=response.status_code,
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create Notion webhook: {e}", exc_info=True)
        return Response(
            {"error": f"API request failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def notion_webhook_delete(request, webhook_id):
    """
    Delete a Notion webhook subscription.

    Args:
        webhook_id: Notion webhook ID to delete

    Returns:
        {"success": bool, "message": str}
    """
    try:
        subscription = NotionWebhookSubscription.objects.get(
            user=request.user, webhook_id=webhook_id
        )
    except NotionWebhookSubscription.DoesNotExist:
        return Response(
            {"error": "Webhook not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Get Notion access token
    access_token = OAuthManager.get_valid_token(request.user, "notion")
    if not access_token:
        # Just delete locally if token expired
        subscription.mark_revoked()
        logger.warning(
            f"Deleted Notion webhook {webhook_id} locally (token expired for user {request.user.username})"
        )
        return Response(
            {
                "success": True,
                "message": "Webhook deleted locally (Notion token expired)",
            }
        )

    # Delete webhook via Notion API
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Notion-Version": "2022-06-28",
    }

    try:
        response = requests.delete(
            f"https://api.notion.com/v1/webhooks/{webhook_id}",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            subscription.mark_revoked()
            logger.info(
                f"Deleted Notion webhook {webhook_id} for user {request.user.username}"
            )
            return Response(
                {
                    "success": True,
                    "message": "Webhook deleted successfully",
                }
            )
        else:
            logger.error(
                f"Failed to delete Notion webhook: {response.status_code} - {response.text}"
            )
            # Delete locally anyway
            subscription.mark_revoked()
            return Response(
                {
                    "success": True,
                    "message": "Webhook deleted locally (Notion API error)",
                }
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to delete Notion webhook: {e}", exc_info=True)
        subscription.mark_revoked()
        return Response(
            {
                "success": True,
                "message": "Webhook deleted locally (API unreachable)",
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notion_webhook_list(request):
    """
    List all Notion webhook subscriptions for the authenticated user.

    Returns:
        {
            "subscriptions": [
                {
                    "webhook_id": str,
                    "workspace_id": str,
                    "page_id": str,
                    "database_id": str,
                    "event_types": list,
                    "status": str,
                    "created_at": datetime,
                    "event_count": int,
                    "last_event_at": datetime
                }
            ],
            "total": int
        }
    """
    subscriptions = NotionWebhookSubscription.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    return Response(
        {
            "subscriptions": [
                {
                    "webhook_id": sub.webhook_id,
                    "workspace_id": sub.workspace_id,
                    "page_id": sub.page_id,
                    "database_id": sub.database_id,
                    "event_types": sub.event_types,
                    "status": sub.status,
                    "created_at": sub.created_at.isoformat(),
                    "event_count": sub.event_count,
                    "last_event_at": (
                        sub.last_event_at.isoformat() if sub.last_event_at else None
                    ),
                }
                for sub in subscriptions
            ],
            "total": subscriptions.count(),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notion_webhook_status_for_area(request, area_id):
    """
    Get webhook status for a specific Area.
    
    Used by frontend to display webhook status badge for each Area.
    
    Args:
        area_id: ID of the Area to check
        
    Returns:
        {
            "has_webhook": bool,
            "webhook_id": str | null,
            "status": "active" | "inactive" | "pending" | "failed",
            "event_count": int,
            "last_event_at": datetime | null,
            "created_at": datetime | null
        }
    """
    from .models import Area
    
    try:
        # Verify user owns this Area
        area = Area.objects.get(id=area_id, owner=request.user)
        
        # Find webhook associated with this Area
        webhook = NotionWebhookSubscription.objects.filter(
            area=area,
            status=NotionWebhookSubscription.Status.ACTIVE
        ).first()
        
        if webhook:
            return Response({
                "has_webhook": True,
                "webhook_id": webhook.webhook_id,
                "status": webhook.status,
                "event_count": webhook.event_count,
                "last_event_at": webhook.last_event_at.isoformat() if webhook.last_event_at else None,
                "created_at": webhook.created_at.isoformat(),
            })
        else:
            # No webhook found - Area is in polling mode
            return Response({
                "has_webhook": False,
                "webhook_id": None,
                "status": "inactive",
                "event_count": 0,
                "last_event_at": None,
                "created_at": None,
            })
    
    except Area.DoesNotExist:
        return Response(
            {"error": "Area not found"},
            status=status.HTTP_404_NOT_FOUND
        )
