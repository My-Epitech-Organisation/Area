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
