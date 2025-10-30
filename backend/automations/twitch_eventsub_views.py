##
## EPITECH PROJECT, 2025
## Area
## File description:
## twitch_eventsub_views
##

"""
Twitch EventSub webhook subscription management views.

Provides API endpoints for:
- Checking user's EventSub subscription status
- Creating EventSub subscriptions
- Deleting EventSub subscriptions
- Managing subscription lifecycle

Similar to GitHub App integration but using Twitch EventSub API.
"""

import logging
import requests
from typing import Optional

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import TwitchEventSubSubscription

logger = logging.getLogger(__name__)


def get_twitch_client_id() -> str:
    """
    Get Twitch Client ID from OAUTH2_PROVIDERS configuration.

    Returns:
        Twitch Client ID

    Raises:
        ValueError: If Twitch is not configured
    """
    twitch_config = settings.OAUTH2_PROVIDERS.get("twitch", {})
    client_id = twitch_config.get("client_id")

    if not client_id:
        raise ValueError("Twitch Client ID not configured in OAUTH2_PROVIDERS")

    return client_id


def get_twitch_access_token(user) -> Optional[str]:
    """
    Get valid Twitch access token for user.

    Returns:
        Access token if user has valid Twitch OAuth connection, None otherwise
    """
    from users.oauth.manager import OAuthManager

    try:
        access_token = OAuthManager.get_valid_token(user, "twitch")
        return access_token
    except Exception as e:
        logger.warning(f"Failed to get Twitch token for user {user.username}: {e}")
        return None


def get_twitch_user_id(access_token: str) -> Optional[dict]:
    """
    Get Twitch user ID and username from access token.

    Returns:
        Dict with 'id' and 'login' keys, or None on error
    """
    try:
        client_id = get_twitch_client_id()
        response = requests.get(
            "https://api.twitch.tv/helix/users",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": client_id,
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            user_data = data["data"][0]
            return {
                "id": user_data["id"],
                "login": user_data["login"]
            }
        return None
    except Exception as e:
        logger.error(f"Failed to get Twitch user info: {e}")
        return None


def create_eventsub_subscription(
    access_token: str,
    subscription_type: str,
    condition: dict
) -> Optional[dict]:
    """
    Create a Twitch EventSub subscription.

    Args:
        access_token: User's Twitch OAuth token
        subscription_type: EventSub subscription type (e.g., 'stream.online')
        condition: Condition parameters (e.g., {'broadcaster_user_id': '12345'})

    Returns:
        Subscription data dict or None on error
    """
    webhook_url = f"{settings.BACKEND_URL}/webhooks/twitch/"

    payload = {
        "type": subscription_type,
        "version": "1",
        "condition": condition,
        "transport": {
            "method": "webhook",
            "callback": webhook_url,
            "secret": settings.TWITCH_WEBHOOK_SECRET
        }
    }

    try:
        client_id = get_twitch_client_id()
        response = requests.post(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": client_id,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            return data["data"][0]
        return None
    except Exception as e:
        logger.error(f"Failed to create EventSub subscription: {e}")
        if hasattr(e, 'response'):
            logger.error(f"Response: {e.response.text}")
        return None


def delete_eventsub_subscription(access_token: str, subscription_id: str) -> bool:
    """
    Delete a Twitch EventSub subscription.

    Returns:
        True if successful, False otherwise
    """
    try:
        client_id = get_twitch_client_id()
        response = requests.delete(
            f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": client_id,
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to delete EventSub subscription {subscription_id}: {e}")
        return False


@extend_schema(
    summary="Get Twitch EventSub subscription status",
    description="Check if user has active Twitch EventSub subscriptions",
    responses={
        200: OpenApiResponse(description="Subscription status retrieved"),
        401: OpenApiResponse(description="Not authenticated"),
    }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def twitch_eventsub_status(request: Request) -> Response:
    """
    Get user's Twitch EventSub subscription status.

    Returns:
        {
            "has_subscriptions": bool,
            "subscriptions": [
                {
                    "id": str,
                    "type": str,
                    "status": str,
                    "broadcaster_login": str,
                    "broadcaster_user_id": str
                }
            ]
        }
    """
    subscriptions = TwitchEventSubSubscription.objects.filter(
        user=request.user
    ).values(
        "id",
        "subscription_id",
        "subscription_type",
        "status",
        "broadcaster_login",
        "broadcaster_user_id",
        "created_at"
    )

    return Response({
        "has_subscriptions": subscriptions.exists(),
        "subscriptions": list(subscriptions)
    })


@extend_schema(
    summary="Create Twitch EventSub subscription",
    description="Create a new EventSub subscription for real-time Twitch events",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "subscription_type": {
                    "type": "string",
                    "enum": [
                        "stream.online",
                        "stream.offline",
                        "channel.update",
                        "channel.follow",
                        "channel.subscribe"
                    ]
                },
                "broadcaster_user_id": {"type": "string"}
            },
            "required": ["subscription_type"]
        }
    },
    responses={
        201: OpenApiResponse(description="Subscription created"),
        400: OpenApiResponse(description="Invalid request or Twitch not connected"),
        500: OpenApiResponse(description="Failed to create subscription"),
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def twitch_eventsub_subscribe(request: Request) -> Response:
    """
    Create a Twitch EventSub subscription.

    Request body:
        {
            "subscription_type": "stream.online",
            "broadcaster_user_id": "12345"  # Optional, defaults to authenticated user
        }
    """
    subscription_type = request.data.get("subscription_type")
    broadcaster_user_id = request.data.get("broadcaster_user_id")

    if not subscription_type:
        return Response(
            {"error": "subscription_type is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get user's Twitch access token
    access_token = get_twitch_access_token(request.user)
    if not access_token:
        return Response(
            {"error": "Twitch account not connected. Please connect your Twitch account first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get user's Twitch info if broadcaster_user_id not provided
    if not broadcaster_user_id:
        twitch_user = get_twitch_user_id(access_token)
        if not twitch_user:
            return Response(
                {"error": "Failed to get Twitch user info"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        broadcaster_user_id = twitch_user["id"]
        broadcaster_login = twitch_user["login"]
    else:
        # If broadcaster_user_id provided, fetch their username
        try:
            response = requests.get(
                f"https://api.twitch.tv/helix/users?id={broadcaster_user_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Client-Id": settings.TWITCH_CLIENT_ID,
                },
                timeout=10
            )
            response.raise_for_status()
            user_data = response.json().get("data", [])
            if user_data:
                broadcaster_login = user_data[0]["login"]
            else:
                broadcaster_login = broadcaster_user_id
        except Exception as e:
            logger.warning(f"Failed to fetch broadcaster username: {e}")
            broadcaster_login = broadcaster_user_id

    # Check if subscription already exists
    existing = TwitchEventSubSubscription.objects.filter(
        user=request.user,
        subscription_type=subscription_type,
        broadcaster_user_id=broadcaster_user_id
    ).first()

    if existing and existing.is_active():
        return Response(
            {
                "message": "Subscription already exists",
                "subscription": {
                    "id": existing.id,
                    "subscription_id": existing.subscription_id,
                    "type": existing.subscription_type,
                    "status": existing.status
                }
            },
            status=status.HTTP_200_OK
        )

    # Build condition based on subscription type
    condition = {"broadcaster_user_id": broadcaster_user_id}

    # For channel.follow, we need user_id (the follower)
    if subscription_type == "channel.follow":
        condition["moderator_user_id"] = broadcaster_user_id

    # Create EventSub subscription via Twitch API
    subscription_data = create_eventsub_subscription(
        access_token,
        subscription_type,
        condition
    )

    if not subscription_data:
        return Response(
            {"error": "Failed to create EventSub subscription with Twitch API"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Save to database
    with transaction.atomic():
        if existing:
            # Update existing inactive subscription
            existing.subscription_id = subscription_data["id"]
            existing.status = subscription_data["status"]
            existing.condition = subscription_data["condition"]
            existing.cost = subscription_data.get("cost", 0)
            existing.broadcaster_login = broadcaster_login
            existing.broadcaster_user_id = broadcaster_user_id
            existing.save()
            subscription = existing
        else:
            subscription = TwitchEventSubSubscription.objects.create(
                user=request.user,
                subscription_id=subscription_data["id"],
                subscription_type=subscription_type,
                status=subscription_data["status"],
                condition=subscription_data["condition"],
                broadcaster_login=broadcaster_login,
                broadcaster_user_id=broadcaster_user_id,
                cost=subscription_data.get("cost", 0)
            )

    logger.info(
        f"Created Twitch EventSub subscription for {request.user.username}: "
        f"{subscription_type} ({broadcaster_login})"
    )

    return Response(
        {
            "message": "EventSub subscription created successfully",
            "subscription": {
                "id": subscription.id,
                "subscription_id": subscription.subscription_id,
                "type": subscription.subscription_type,
                "status": subscription.status,
                "broadcaster_login": subscription.broadcaster_login
            }
        },
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    summary="Delete Twitch EventSub subscription",
    description="Delete an existing EventSub subscription",
    responses={
        200: OpenApiResponse(description="Subscription deleted"),
        404: OpenApiResponse(description="Subscription not found"),
        500: OpenApiResponse(description="Failed to delete subscription"),
    }
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def twitch_eventsub_unsubscribe(request: Request, subscription_id: int) -> Response:
    """
    Delete a Twitch EventSub subscription.

    Args:
        subscription_id: Database ID of the subscription to delete
    """
    try:
        subscription = TwitchEventSubSubscription.objects.get(
            id=subscription_id,
            user=request.user
        )
    except TwitchEventSubSubscription.DoesNotExist:
        return Response(
            {"error": "Subscription not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get user's Twitch access token
    access_token = get_twitch_access_token(request.user)
    if not access_token:
        return Response(
            {"error": "Twitch account not connected"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Delete from Twitch API
    success = delete_eventsub_subscription(access_token, subscription.subscription_id)

    # Delete from database even if API call failed (cleanup)
    subscription.delete()

    if success:
        logger.info(
            f"Deleted Twitch EventSub subscription for {request.user.username}: "
            f"{subscription.subscription_type}"
        )
        return Response(
            {"message": "Subscription deleted successfully"},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message": "Subscription deleted from database, but Twitch API deletion failed"},
            status=status.HTTP_200_OK
        )
