##
## EPITECH PROJECT, 2025
## Area
## File description:
## notion_webhook_helpers - Helper functions for auto-managing Notion webhooks
##

"""
Helper functions for automatic Notion webhook management.

This module provides GitHub App-like functionality where webhooks are
automatically created and managed when users create Areas with Notion actions.
"""

import logging

import requests

from django.conf import settings

from users.models import ServiceToken

from .models import NotionWebhookSubscription

logger = logging.getLogger(__name__)


def auto_create_notion_webhook_for_area(area):
    """
    Automatically create a Notion webhook when an Area is created/updated.

    This provides GitHub App-like UX where webhooks are managed automatically.

    Args:
        area: Area instance with Notion action

    Returns:
        tuple: (success: bool, webhook_subscription: NotionWebhookSubscription or None, error: str or None)

    Flow:
        1. Check if Area uses Notion service
        2. Extract page_id or database_id from action_config
        3. Check if user has Notion OAuth token
        4. Check if webhook already exists for this page/database
        5. Create webhook via Notion API
        6. Store webhook subscription in database
    """
    try:
        # Step 1: Check if this is a Notion action
        if area.action.service.name.lower() != "notion":
            return (False, None, "Not a Notion action")

        # Step 2: Extract page_id or database_id from action_config
        page_id = area.action_config.get("page_id")
        database_id = area.action_config.get("database_id")

        if not page_id and not database_id:
            logger.info(
                f"Area #{area.id} has no page_id or database_id in config, "
                "skipping webhook creation"
            )
            return (False, None, "No page_id or database_id in action_config")

        # Step 3: Get user's Notion OAuth token
        try:
            token = ServiceToken.objects.get(user=area.owner, service_name="notion")
        except ServiceToken.DoesNotExist:
            logger.error(
                f"User {area.owner.email} has no Notion token, "
                "cannot create webhook for Area #{area.id}"
            )
            return (False, None, "User not connected to Notion")

        # Step 4: Check if webhook already exists
        existing = NotionWebhookSubscription.objects.filter(
            user=area.owner,
            status=NotionWebhookSubscription.Status.ACTIVE,
        )

        if page_id:
            existing = existing.filter(page_id=page_id)
        if database_id:
            existing = existing.filter(database_id=database_id)

        if existing.exists():
            logger.info(
                f"Webhook already exists for page_id={page_id} "
                f"database_id={database_id}, skipping creation"
            )
            return (True, existing.first(), None)

        # Step 5: Create webhook via Notion API
        webhook_url = f"{settings.BACKEND_URL}/webhooks/notion/"
        webhook_secret = _get_notion_webhook_secret()

        # Determine event types based on what's configured
        event_types = []
        if page_id:
            event_types.append("page.updated")
        if database_id:
            event_types.append("database.updated")

        # Call Notion API to create webhook
        response = requests.post(
            "https://api.notion.com/v1/webhooks",
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
            json={
                "url": webhook_url,
                "event_types": event_types,
                **({"page_id": page_id} if page_id else {}),
                **({"database_id": database_id} if database_id else {}),
            },
            timeout=10,
        )

        if not response.ok:
            error_msg = f"Notion API error {response.status_code}: {response.text}"
            logger.error(
                f"Failed to create webhook for Area #{area.id}: {error_msg}"
            )
            return (False, None, error_msg)

        webhook_data = response.json()

        # Step 6: Store webhook subscription
        webhook_subscription = NotionWebhookSubscription.objects.create(
            user=area.owner,
            webhook_id=webhook_data.get("id"),
            workspace_id=webhook_data.get("workspace_id", ""),
            page_id=page_id or "",
            database_id=database_id or "",
            event_types=event_types,
            status=NotionWebhookSubscription.Status.ACTIVE,
        )

        logger.info(
            f"✅ Auto-created Notion webhook {webhook_subscription.webhook_id} "
            f"for Area #{area.id} (user: {area.owner.email})"
        )

        return (True, webhook_subscription, None)

    except requests.RequestException as e:
        error_msg = f"Network error creating webhook: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return (False, None, error_msg)

    except Exception as e:
        error_msg = f"Unexpected error creating webhook: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return (False, None, error_msg)


def _get_notion_webhook_secret():
    """Get Notion webhook secret from settings."""
    import json

    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", "{}")
    if isinstance(webhook_secrets, str):
        try:
            webhook_secrets = json.loads(webhook_secrets)
        except json.JSONDecodeError:
            webhook_secrets = {}

    return webhook_secrets.get("notion", "")


def delete_notion_webhook_for_area(area):
    """
    Delete Notion webhook when an Area is deleted.

    Args:
        area: Area instance being deleted

    Returns:
        bool: True if webhook was deleted, False otherwise
    """
    try:
        # Find webhooks for this area's page/database
        page_id = area.action_config.get("page_id")
        database_id = area.action_config.get("database_id")

        if not page_id and not database_id:
            return False

        webhooks = NotionWebhookSubscription.objects.filter(
            user=area.owner,
            status=NotionWebhookSubscription.Status.ACTIVE,
        )

        if page_id:
            webhooks = webhooks.filter(page_id=page_id)
        if database_id:
            webhooks = webhooks.filter(database_id=database_id)

        # Check if other Areas are using the same webhook
        from .models import Area

        other_areas = Area.objects.filter(
            owner=area.owner, action__service__name__iexact="notion"
        ).exclude(id=area.id)

        for other_area in other_areas:
            other_page_id = other_area.action_config.get("page_id")
            other_database_id = other_area.action_config.get("database_id")

            if (page_id and other_page_id == page_id) or (
                database_id and other_database_id == database_id
            ):
                # Another Area is using this webhook, don't delete
                logger.info(
                    f"Webhook for page_id={page_id} database_id={database_id} "
                    f"still used by Area #{other_area.id}, not deleting"
                )
                return False

        # No other Areas using this webhook, safe to delete
        for webhook in webhooks:
            try:
                # Get user's token
                token = ServiceToken.objects.get(
                    user=area.owner, service_name="notion"
                )

                # Call Notion API to delete webhook
                response = requests.delete(
                    f"https://api.notion.com/v1/webhooks/{webhook.webhook_id}",
                    headers={
                        "Authorization": f"Bearer {token.access_token}",
                        "Notion-Version": "2022-06-28",
                    },
                    timeout=10,
                )

                if response.ok:
                    webhook.delete()
                    logger.info(
                        f"✅ Auto-deleted Notion webhook {webhook.webhook_id} "
                        f"for deleted Area #{area.id}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to delete webhook {webhook.webhook_id} "
                        f"from Notion API: {response.status_code}"
                    )
                    # Mark as revoked instead
                    webhook.status = NotionWebhookSubscription.Status.REVOKED
                    webhook.save()

            except ServiceToken.DoesNotExist:
                logger.warning(
                    f"User {area.owner.email} has no Notion token, "
                    "marking webhook as revoked"
                )
                webhook.status = NotionWebhookSubscription.Status.REVOKED
                webhook.save()

            except Exception as e:
                logger.error(f"Error deleting webhook: {str(e)}", exc_info=True)

        return False

    except Exception as e:
        logger.error(
            f"Error in delete_notion_webhook_for_area: {str(e)}", exc_info=True
        )
        return False
