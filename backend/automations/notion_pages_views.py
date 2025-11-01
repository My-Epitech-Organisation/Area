##
## EPITECH PROJECT, 2025
## Area
## File description:
## notion_pages_views
##

"""
API endpoints for Notion pages/databases listing.

These views provide GitHub App-like UX by allowing users to select
from their authorized Notion pages instead of manually entering UUIDs.
"""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import NotionPage

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notion_pages_list(request):
    """
    List user's authorized Notion pages and databases.

    GET /api/notion-pages/

    Returns all pages/databases the user granted access to during OAuth.
    This enables dropdown/selector UI instead of manual UUID entry.

    Query Parameters:
        - type: Filter by 'page' or 'database' (optional)
        - search: Search in page titles (optional)

    Returns:
        {
            "count": int,
            "pages": [
                {
                    "page_id": str,
                    "page_type": "page"|"database",
                    "title": str,
                    "workspace_id": str,
                    "icon": dict|null,
                    "url": str,
                    "parent": dict|null,
                    "is_accessible": bool,
                    "updated_at": datetime
                }
            ]
        }
    """
    # Get query parameters
    page_type_filter = request.query_params.get("type")
    search_query = request.query_params.get("search", "").strip()

    # Start with user's pages
    pages = NotionPage.objects.filter(user=request.user, is_accessible=True)

    # Apply filters
    if page_type_filter and page_type_filter in ["page", "database"]:
        pages = pages.filter(page_type=page_type_filter)

    if search_query:
        pages = pages.filter(title__icontains=search_query)

    # Order by most recently updated
    pages = pages.order_by("-updated_at")

    # Serialize data
    pages_data = [
        {
            "page_id": page.page_id,
            "page_type": page.page_type,
            "title": page.title,
            "workspace_id": page.workspace_id,
            "icon": page.icon,
            "url": page.url,
            "parent": page.parent,
            "is_accessible": page.is_accessible,
            "updated_at": page.updated_at.isoformat(),
        }
        for page in pages
    ]

    return Response(
        {
            "count": len(pages_data),
            "pages": pages_data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def notion_pages_refresh(request):
    """
    Manually refresh user's Notion pages from API.

    POST /api/notion-pages/refresh/

    Useful when user has granted access to new pages since initial OAuth.
    Calls Notion /v1/search and updates NotionPage records.

    Returns:
        {
            "success": bool,
            "pages_synced": int,
            "pages_created": int,
            "pages_updated": int,
            "message": str
        }
    """
    try:
        from users.models import ServiceToken

        # Get user's Notion token
        try:
            token = ServiceToken.objects.get(user=request.user, service_name="notion")
        except ServiceToken.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": "notion_not_connected",
                    "message": "Notion account not connected. Please connect first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Call the same fetch logic used in OAuth callback
        from users.oauth_views import OAuthCallbackView

        callback_view = OAuthCallbackView()
        callback_view._fetch_and_store_notion_pages(request.user, token.access_token)

        # Count results
        pages_count = NotionPage.objects.filter(
            user=request.user, is_accessible=True
        ).count()

        return Response(
            {
                "success": True,
                "pages_synced": pages_count,
                "message": f"Successfully refreshed {pages_count} Notion pages",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(
            f"Error refreshing Notion pages for {request.user.email}: {str(e)}",
            exc_info=True,
        )
        return Response(
            {
                "success": False,
                "error": "refresh_failed",
                "message": f"Failed to refresh pages: {str(e)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
