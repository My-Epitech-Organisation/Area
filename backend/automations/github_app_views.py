"""
API endpoints for GitHub App integration.

These views handle:
- Checking if user has installed the GitHub App
- Linking installations to users
- Getting installation status
"""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.conf import settings

from .models import GitHubAppInstallation

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def github_app_status(request):
    """
    Check if user has installed GitHub App.

    Returns:
        {
            "installed": bool,
            "installations": [
                {
                    "id": int,
                    "account": str,
                    "type": str,
                    "repositories_count": int,
                    "installed_at": datetime
                }
            ],
            "install_url": str
        }
    """
    installations = GitHubAppInstallation.objects.filter(
        user=request.user, is_active=True
    )

    has_installation = installations.exists()
    app_name = getattr(settings, "GITHUB_APP_NAME", "area-automation")

    return Response(
        {
            "installed": has_installation,
            "installations": [
                {
                    "id": inst.installation_id,
                    "account": inst.account_login,
                    "type": inst.account_type,
                    "repositories_count": len(inst.repositories),
                    "repositories": inst.repositories,
                    "installed_at": inst.installed_at.isoformat(),
                }
                for inst in installations
            ],
            "install_url": f"https://github.com/apps/{app_name}/installations/new",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def github_app_link_installation(request):
    """
    Link a GitHub App installation to the authenticated user.

    This is called after the user installs the app and is redirected back.
    Creates a placeholder installation that will be updated by the webhook.

    Request body:
        {
            "installation_id": int
        }

    Returns:
        {
            "success": bool,
            "installation_id": int
        }
    """
    installation_id = request.data.get("installation_id")

    if not installation_id:
        return Response(
            {"error": "installation_id required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        installation_id = int(installation_id)
    except (ValueError, TypeError):
        return Response(
            {"error": "installation_id must be an integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if installation exists
    installation = GitHubAppInstallation.objects.filter(
        installation_id=installation_id
    ).first()

    if not installation:
        # Create placeholder installation - webhook will update with details
        installation = GitHubAppInstallation.objects.create(
            installation_id=installation_id,
            user=request.user,
            account_login=request.user.username or "GitHub User",
            account_type="User",
            repositories=[],
            is_active=True,
        )
        logger.info(
            f"Created installation {installation_id} for user {request.user.username}, "
            "waiting for webhook to populate details"
        )
    else:
        # Update user link if needed
        if installation.user != request.user:
            installation.user = request.user
            installation.save()
            logger.info(
                f"Linked installation {installation_id} to user {request.user.username}"
            )

    return Response(
        {
            "success": True,
            "installation_id": installation_id,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def github_app_repositories(request):
    """
    Get all repositories where user has installed the GitHub App.

    Returns:
        {
            "repositories": [
                {
                    "full_name": str,
                    "installation_id": int,
                    "account": str
                }
            ]
        }
    """
    installations = GitHubAppInstallation.objects.filter(
        user=request.user, is_active=True
    )

    repositories = []
    for inst in installations:
        for repo in inst.repositories:
            repositories.append(
                {
                    "full_name": repo,
                    "installation_id": inst.installation_id,
                    "account": inst.account_login,
                    "account_type": inst.account_type,
                }
            )

    return Response({"repositories": repositories, "total_count": len(repositories)})
