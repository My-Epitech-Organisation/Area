"""
Notion API helper functions.

This module contains utility functions for interacting with the Notion API,
including UUID extraction, database search, and page search.
"""

import logging
import re
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def extract_notion_uuid(identifier: str) -> Optional[str]:
    """
    Extract UUID from a Notion identifier (URL or direct UUID).

    Args:
        identifier: Notion URL or UUID string

    Returns:
        The extracted UUID with dashes, or None if invalid

    Examples:
        >>> extract_notion_uuid("https://www.notion.so/MyPage-29cf551e5b15809898e8fb5b67b58b5a")
        '29cf551e-5b15-8098-98e8-fb5b67b58b5a'

        >>> extract_notion_uuid("29cf551e5b15809898e8fb5b67b58b5a")
        '29cf551e-5b15-8098-98e8-fb5b67b58b5a'

        >>> extract_notion_uuid("29cf551e-5b15-80e7-9bc0-000c4bb72974")
        '29cf551e-5b15-80e7-9bc0-000c4bb72974'

        >>> extract_notion_uuid("My Page Name")
        None
    """
    if not identifier:
        return None

    # If it's already a UUID with dashes, return it
    uuid_pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    if re.match(uuid_pattern, identifier):
        return identifier

    # Check if it's a 32-character UUID without dashes
    uuid_no_dashes_pattern = r"^[a-f0-9]{32}$"
    if re.match(uuid_no_dashes_pattern, identifier):
        # Convert to UUID format with dashes
        return f"{identifier[:8]}-{identifier[8:12]}-{identifier[12:16]}-{identifier[16:20]}-{identifier[20:]}"

    # Try to extract UUID from Notion URL (UUIDs in URLs don't have dashes)
    url_pattern = r"https://www\.notion\.so/.*([a-f0-9]{32})"
    match = re.search(url_pattern, identifier)
    if match:
        uuid_no_dashes = match.group(1)
        # Convert to UUID format with dashes
        if len(uuid_no_dashes) == 32:
            return f"{uuid_no_dashes[:8]}-{uuid_no_dashes[8:12]}-{uuid_no_dashes[12:16]}-{uuid_no_dashes[16:20]}-{uuid_no_dashes[20:]}"

    return None


def find_notion_database_by_name(access_token: str, database_name: str) -> Optional[str]:
    """
    Search for a Notion database by name in the user's workspace.

    Args:
        access_token: Valid Notion API token
        database_name: Name of the database to search for

    Returns:
        Database UUID if found, None otherwise
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Search for databases in the workspace
    search_payload = {
        "query": database_name,
        "filter": {
            "property": "object",
            "value": "database"
        },
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    }

    try:
        response = requests.post(
            "https://api.notion.com/v1/search",
            json=search_payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            search_results = response.json()
            databases = search_results.get("results", [])

            # Look for exact name match first
            for db in databases:
                db_title = extract_database_title(db)
                if db_title and db_title.lower() == database_name.lower():
                    logger.info(f"[REACTION NOTION] Found database '{db_title}' with ID: {db['id']}")
                    return db["id"]

            # If no exact match, return the first partial match
            if databases:
                db_title = extract_database_title(databases[0])
                logger.info(f"[REACTION NOTION] Using partial match '{db_title}' for search '{database_name}'")
                return databases[0]["id"]

            logger.warning(f"[REACTION NOTION] No database found with name: {database_name}")
            return None

        else:
            logger.error(f"[REACTION NOTION] Search API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"[REACTION NOTION] Search request failed: {e}")
        return None


def extract_database_title(database: dict) -> Optional[str]:
    """
    Extract the title from a Notion database object.

    Args:
        database: Notion database object from API response

    Returns:
        Database title or None if not found
    """
    try:
        title_property = database.get("title", [])
        if title_property:
            return "".join([part.get("plain_text", "") for part in title_property])
        return None
    except Exception:
        return None


def find_notion_page_by_name(access_token: str, page_name: str) -> Optional[str]:
    """
    Search for a Notion page by name in the user's workspace.

    Args:
        access_token: Valid Notion API token
        page_name: Name of the page to search for

    Returns:
        Page UUID if found, None otherwise
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Search for pages in the workspace
    search_payload = {
        "query": page_name,
        "filter": {
            "property": "object",
            "value": "page"
        },
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    }

    try:
        response = requests.post(
            "https://api.notion.com/v1/search",
            json=search_payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            search_results = response.json()
            pages = search_results.get("results", [])

            # Look for exact name match first
            for page in pages:
                page_title = extract_page_title(page)
                if page_title and page_title.lower() == page_name.lower():
                    logger.info(f"[REACTION NOTION] Found page '{page_title}' with ID: {page['id']}")
                    return page["id"]

            # If no exact match, return the first partial match
            if pages:
                page_title = extract_page_title(pages[0])
                logger.info(f"[REACTION NOTION] Using partial match '{page_title}' for search '{page_name}'")
                return pages[0]["id"]

            logger.warning(f"[REACTION NOTION] No page found with name: {page_name}")
            return None

        else:
            logger.error(f"[REACTION NOTION] Search API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"[REACTION NOTION] Search request failed: {e}")
        return None


def extract_page_title(page: dict) -> str:
    """
    Extract the title from a Notion page object.

    Args:
        page: Notion page object from API response

    Returns:
        str: Page title or "Untitled" if no title found
    """
    try:
        properties = page.get("properties", {})

        # Look for title property (most common)
        if "title" in properties:
            title_property = properties["title"]
            if title_property.get("type") == "title":
                title_parts = title_property.get("title", [])
                if title_parts:
                    return "".join([part.get("plain_text", "") for part in title_parts])

        # Look for Name property (common in databases)
        if "Name" in properties:
            name_property = properties["Name"]
            if name_property.get("type") == "title":
                name_parts = name_property.get("title", [])
                if name_parts:
                    return "".join([part.get("plain_text", "") for part in name_parts])

        # Fallback to page ID if no title found
        return f"Untitled Page ({page.get('id', 'unknown')[:8]})"

    except Exception:
        return f"Untitled Page ({page.get('id', 'unknown')[:8]})"


def extract_database_item_title(item: dict) -> str:
    """
    Extract the title/name from a Notion database item.

    Args:
        item: Notion database item from API response

    Returns:
        str: Item title or "Untitled Item" if no title found
    """
    try:
        properties = item.get("properties", {})

        # Look for Name property (most common in databases)
        if "Name" in properties:
            name_property = properties["Name"]
            if name_property.get("type") == "title":
                name_parts = name_property.get("title", [])
                if name_parts:
                    return "".join([part.get("plain_text", "") for part in name_parts])

        # Look for title property
        if "title" in properties:
            title_property = properties["title"]
            if title_property.get("type") == "title":
                title_parts = title_property.get("title", [])
                if title_parts:
                    return "".join([part.get("plain_text", "") for part in title_parts])

        # Fallback to item ID
        return f"Untitled Item ({item.get('id', 'unknown')[:8]})"

    except Exception:
        return f"Untitled Item ({item.get('id', 'unknown')[:8]})"


def auto_create_notion_webhook(area, user) -> bool:
    """
    Automatically create a Notion webhook for an Area.
    
    This function is called when an Area with Notion action is created/updated.
    It creates a webhook subscription via Notion API and saves it to database.
    
    Args:
        area: Area instance with Notion action
        user: User instance who owns the Area
        
    Returns:
        bool: True if webhook created successfully, False otherwise
    """
    from django.conf import settings
    from ..models import NotionWebhookSubscription
    from users.models import ServiceToken
    
    try:
        # Get user's Notion OAuth token
        oauth_token = ServiceToken.objects.filter(
            user=user,
            service_name='notion'
        ).first()
        
        if not oauth_token or oauth_token.is_expired:
            logger.warning(f"No valid Notion OAuth token for user {user.id}")
            return False
        
        # Extract page_id or database_id from action_config
        action_config = area.action_config or {}
        page_id = action_config.get('page_id', '')
        database_id = action_config.get('database_id', '')
        
        # Extract UUID if it's a URL
        if page_id:
            page_id = extract_notion_uuid(page_id) or page_id
        if database_id:
            database_id = extract_notion_uuid(database_id) or database_id
        
        if not page_id and not database_id:
            logger.warning(f"Area {area.id} has no page_id or database_id in action_config")
            return False
        
        # Check if webhook already exists for this Area
        existing = NotionWebhookSubscription.objects.filter(
            area=area,
            status=NotionWebhookSubscription.Status.ACTIVE
        ).first()
        
        if existing:
            logger.info(f"Webhook already exists for Area {area.id}")
            return True
        
        # Determine event types based on action
        action_name = area.action.name.lower()
        if 'page' in action_name:
            event_types = ['page.updated']
            resource_id = page_id
            resource_type = 'page'
        elif 'database' in action_name:
            event_types = ['database.updated']
            resource_id = database_id
            resource_type = 'database'
        else:
            event_types = ['page.updated', 'database.updated']
            resource_id = page_id or database_id
            resource_type = 'page' if page_id else 'database'
        
        # Get webhook secret from settings
        webhook_secrets = settings.WEBHOOK_SECRETS or {}
        notion_secret = webhook_secrets.get('notion', '')
        
        if not notion_secret:
            logger.error("WEBHOOK_SECRETS['notion'] not configured")
            return False
        
        # Prepare webhook creation payload
        backend_url = settings.BACKEND_URL.rstrip('/')
        webhook_url = f"{backend_url}/webhooks/notion/"
        
        headers = {
            "Authorization": f"Bearer {oauth_token.access_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        payload = {
            "url": webhook_url,
            "event_types": event_types,
        }
        
        # Add resource filter if we have a specific page/database
        if resource_id:
            payload["filter"] = {
                "object": resource_type,
                "id": resource_id
            }
        
        # Create webhook via Notion API
        response = requests.post(
            "https://api.notion.com/v1/webhooks",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to create Notion webhook: {response.status_code} - {response.text}")
            return False
        
        webhook_data = response.json()
        webhook_id = webhook_data.get('id')
        workspace_id = webhook_data.get('workspace_id', '')
        
        if not webhook_id:
            logger.error(f"No webhook_id in Notion API response: {webhook_data}")
            return False
        
        # Save webhook subscription to database
        NotionWebhookSubscription.objects.create(
            user=user,
            area=area,
            webhook_id=webhook_id,
            workspace_id=workspace_id,
            page_id=page_id,
            database_id=database_id,
            event_types=event_types,
            status=NotionWebhookSubscription.Status.ACTIVE
        )
        
        logger.info(f"✅ Auto-created Notion webhook {webhook_id} for Area {area.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to auto-create Notion webhook for Area {area.id}: {e}", exc_info=True)
        return False


def auto_delete_notion_webhook(area) -> bool:
    """
    Automatically delete Notion webhook(s) associated with an Area.
    
    Called when Area is deleted or its configuration changes.
    
    Args:
        area: Area instance with Notion webhook(s)
        
    Returns:
        bool: True if all webhooks deleted successfully, False otherwise
    """
    from ..models import NotionWebhookSubscription
    from users.models import ServiceToken
    
    try:
        webhooks = NotionWebhookSubscription.objects.filter(
            area=area,
            status=NotionWebhookSubscription.Status.ACTIVE
        )
        
        if not webhooks.exists():
            return True
        
        # Get user's Notion OAuth token
        user = area.owner
        oauth_token = ServiceToken.objects.filter(
            user=user,
            service_name='notion'
        ).first()
        
        if not oauth_token or oauth_token.is_expired:
            logger.warning(f"No valid Notion OAuth token for user {user.id}, marking webhooks as revoked")
            webhooks.update(status=NotionWebhookSubscription.Status.REVOKED)
            return False
        
        headers = {
            "Authorization": f"Bearer {oauth_token.access_token}",
            "Notion-Version": "2022-06-28",
        }
        
        all_deleted = True
        for webhook in webhooks:
            try:
                # Delete webhook via Notion API
                response = requests.delete(
                    f"https://api.notion.com/v1/webhooks/{webhook.webhook_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 204, 404]:
                    # 404 means already deleted, which is fine
                    webhook.delete()
                    logger.info(f"✅ Deleted Notion webhook {webhook.webhook_id} for Area {area.id}")
                else:
                    logger.error(f"Failed to delete webhook {webhook.webhook_id}: {response.status_code}")
                    webhook.mark_revoked()
                    all_deleted = False
                    
            except Exception as e:
                logger.error(f"Error deleting webhook {webhook.webhook_id}: {e}")
                webhook.mark_revoked()
                all_deleted = False
        
        return all_deleted
        
    except Exception as e:
        logger.error(f"Failed to auto-delete Notion webhooks for Area {area.id}: {e}", exc_info=True)
        return False
