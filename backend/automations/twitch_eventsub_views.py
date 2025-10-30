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


def get_backend_webhook_url() -> str:
    """
    Get the backend webhook URL dynamically.

    Returns:
        Backend base URL (e.g., https://areaction.app or http://localhost:8080)
    """
    # First try BACKEND_URL if defined
    backend_url = getattr(settings, "BACKEND_URL", None)
    if backend_url:
        return backend_url

    # Otherwise, construct from ALLOWED_HOSTS
    allowed_hosts = getattr(settings, "ALLOWED_HOSTS", [])
    if allowed_hosts:
        # Filter out localhost/internal hosts for production
        public_hosts = [h for h in allowed_hosts if h not in ["localhost", "127.0.0.1", "0.0.0.0", "*"]]
        if public_hosts:
            # Use first public host with https in production
            protocol = "https" if not settings.DEBUG else "http"
            return f"{protocol}://{public_hosts[0]}"

    # Fallback to localhost for dev
    return "http://localhost:8080"


def get_twitch_webhook_secret() -> str:
    """
    Get Twitch webhook secret from WEBHOOK_SECRETS configuration.

    Returns:
        Twitch webhook secret

    Raises:
        ValueError: If Twitch webhook secret is not configured
    """
    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
    secret = webhook_secrets.get("twitch")

    if not secret:
        raise ValueError(
            "Twitch webhook secret not configured in WEBHOOK_SECRETS. "
            "Set the WEBHOOK_SECRETS environment variable with: "
            '{"twitch": "your_secret_here"}'
        )

    return secret


# Cache for App Access Token (server-to-server authentication)
_app_access_token_cache = {
    "token": None,
    "expires_at": None
}


def get_twitch_app_access_token() -> str:
    """
    Get Twitch App Access Token for server-to-server authentication.
    Required for EventSub subscriptions (different from user OAuth token).

    Uses Client Credentials flow and caches the token until expiration.

    Returns:
        App Access Token

    Raises:
        ValueError: If credentials are not configured or request fails
    """
    from datetime import datetime, timedelta

    # Check if cached token is still valid (with 5 min buffer)
    if _app_access_token_cache["token"] and _app_access_token_cache["expires_at"]:
        if datetime.now() < _app_access_token_cache["expires_at"] - timedelta(minutes=5):
            return _app_access_token_cache["token"]

    # Get credentials
    client_id = get_twitch_client_id()

    # Get client secret from OAUTH2_PROVIDERS
    twitch_config = settings.OAUTH2_PROVIDERS.get("twitch", {})
    client_secret = twitch_config.get("client_secret")

    if not client_secret:
        raise ValueError("Twitch Client Secret not configured in OAUTH2_PROVIDERS")

    # Request App Access Token using Client Credentials flow
    try:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Cache the token
        _app_access_token_cache["token"] = data["access_token"]
        _app_access_token_cache["expires_at"] = datetime.now() + timedelta(seconds=data["expires_in"])

        logger.info("Successfully obtained Twitch App Access Token")
        return data["access_token"]

    except requests.RequestException as e:
        error_msg = f"Failed to obtain Twitch App Access Token: {e}"
        if hasattr(e, "response") and e.response is not None:
            error_msg += f" - Response: {e.response.text}"
        logger.error(error_msg)
        raise ValueError(error_msg)


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
    subscription_type: str,
    condition: dict
) -> Optional[dict]:
    """
    Create a Twitch EventSub subscription using App Access Token.

    Args:
        subscription_type: EventSub subscription type (e.g., 'stream.online')
        condition: Condition parameters (e.g., {'broadcaster_user_id': '12345'})

    Returns:
        Subscription data dict or None on error
    """
    backend_url = get_backend_webhook_url()
    webhook_url = f"{backend_url}/webhooks/twitch/"
    webhook_secret = get_twitch_webhook_secret()

    payload = {
        "type": subscription_type,
        "version": "1",
        "condition": condition,
        "transport": {
            "method": "webhook",
            "callback": webhook_url,
            "secret": webhook_secret
        }
    }

    try:
        # Get App Access Token (required for EventSub subscriptions)
        app_token = get_twitch_app_access_token()
        client_id = get_twitch_client_id()

        response = requests.post(
            "https://api.twitch.tv/helix/eventsub/subscriptions",
            headers={
                "Authorization": f"Bearer {app_token}",
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


def delete_eventsub_subscription(subscription_id: str) -> bool:
    """
    Delete a Twitch EventSub subscription using App Access Token.

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get App Access Token (required for EventSub operations)
        app_token = get_twitch_app_access_token()
        client_id = get_twitch_client_id()

        response = requests.delete(
            f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
            headers={
                "Authorization": f"Bearer {app_token}",
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
            client_id = get_twitch_client_id()
            response = requests.get(
                f"https://api.twitch.tv/helix/users?id={broadcaster_user_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Client-Id": client_id,
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

    # Create EventSub subscription via Twitch API (uses App Access Token internally)
    subscription_data = create_eventsub_subscription(
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
    # Note: We still need user's access_token to verify they own this subscription
    # but the API call itself uses App Access Token internally
    if not access_token:
        return Response(
            {"error": "Twitch account not connected"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Delete from Twitch API (uses App Access Token internally)
    success = delete_eventsub_subscription(subscription.subscription_id)

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
