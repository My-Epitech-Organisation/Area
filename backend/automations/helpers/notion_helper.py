"""
Notion API helper functions.

This module contains utility functions for interacting with the Notion API,
including UUID extraction, database search, and page search.
"""

import re
from typing import Optional


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
