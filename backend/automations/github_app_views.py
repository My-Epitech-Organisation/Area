"""
API endpoints for GitHub App integration.

These views handle:
- Checking if user has installed the GitHub App
- Linking installations to users
- Getting installation status
"""

import logging
import requests

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        user=request.user,
        is_active=True
    )

    has_installation = installations.exists()
    app_name = getattr(settings, "GITHUB_APP_NAME", "area-automation")

    return Response({
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
        "install_url": f"https://github.com/apps/{app_name}/installations/new"
    })


def fetch_installation_details(installation_id: int, user_access_token: str | None = None):
    """
    Fetch installation details from GitHub API.

    Args:
        installation_id: GitHub App installation ID
        user_access_token: Optional user's GitHub OAuth token

    Returns:
        dict with account_login, account_type, and repositories list
        or None if fetch fails
    """
    try:
        # Get user's GitHub token for API access
        if not user_access_token:
            logger.error("No GitHub access token provided")
            return None

        headers = {
            "Authorization": f"token {user_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        logger.info(f"Fetching installation {installation_id} details from GitHub API")

        # List all installations for the user
        response = requests.get(
            "https://api.github.com/user/installations",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            logger.error(
                f"Failed to fetch installations: "
                f"{response.status_code} {response.text[:200]}"
            )
            return None

        data = response.json()
        installations = data.get("installations", [])

        # Find the matching installation
        installation_data = None
        for inst in installations:
            if inst.get("id") == installation_id:
                installation_data = inst
                break

        if not installation_data:
            logger.error(f"Installation {installation_id} not found in user's installations")
            return None

        account = installation_data.get("account", {})
        logger.info(f"Found installation for account: {account.get('login')}")

        # Fetch repositories for this installation
        repos_response = requests.get(
            f"https://api.github.com/user/installations/{installation_id}/repositories",
            headers=headers,
            timeout=10
        )

        repositories = []
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            repositories = [repo["full_name"] for repo in repos_data.get("repositories", [])]
            logger.info(f"Found {len(repositories)} repositories for installation {installation_id}")
        else:
            logger.warning(
                f"Failed to fetch repositories: {repos_response.status_code} "
                f"{repos_response.text[:200]}"
            )

        return {
            "account_login": account.get("login", ""),
            "account_type": account.get("type", "User"),
            "repositories": repositories,
        }

    except Exception as e:
        logger.exception(f"Error fetching installation details: {e}")
        return None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def github_app_link_installation(request):
    """
    Link a GitHub App installation to the authenticated user.

    This is called after the user installs the app and is redirected back.

    Request body:
        {
            "installation_id": int
        }

    Returns:
        {
            "success": bool,
            "installation_id": int,
            "repositories": list
        }
    """
    installation_id = request.data.get("installation_id")

    if not installation_id:
        return Response(
            {"error": "installation_id required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        installation_id = int(installation_id)
    except (ValueError, TypeError):
        return Response(
            {"error": "installation_id must be an integer"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if installation exists
    installation = GitHubAppInstallation.objects.filter(
        installation_id=installation_id
    ).first()

    # Get user's GitHub OAuth token to fetch installation details
    from users.models import ServiceToken
    github_token = ServiceToken.objects.filter(
        user=request.user,
        service_name="github"
    ).first()

    if not github_token:
        return Response(
            {"error": "GitHub OAuth connection required. Please connect your GitHub account first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch installation details from GitHub API
    details = fetch_installation_details(installation_id, github_token.access_token)

    if not details:
        return Response(
            {"error": "Failed to fetch installation details from GitHub. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if not installation:
        # Create new installation with details from GitHub API
        logger.info(
            f"Creating installation {installation_id} for user {request.user.username} "
            f"with {len(details['repositories'])} repositories"
        )

        installation = GitHubAppInstallation.objects.create(
            installation_id=installation_id,
            user=request.user,
            account_login=details["account_login"],
            account_type=details["account_type"],
            repositories=details["repositories"],
            is_active=True,
        )
    else:
        # Update existing installation with fresh data from GitHub API
        installation.user = request.user
        installation.account_login = details["account_login"]
        installation.account_type = details["account_type"]
        installation.repositories = details["repositories"]
        installation.is_active = True
        installation.save()

        logger.info(
            f"Updated installation {installation_id} for user {request.user.username} "
            f"with {len(details['repositories'])} repositories"
        )

    return Response({
        "success": True,
        "installation_id": installation_id,
        "account_login": installation.account_login,
        "repository_count": len(installation.repositories),
        "pending_webhook": False,
    })


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
        user=request.user,
        is_active=True
    )

    repositories = []
    for inst in installations:
        for repo in inst.repositories:
            repositories.append({
                "full_name": repo,
                "installation_id": inst.installation_id,
                "account": inst.account_login,
                "account_type": inst.account_type
            })

    return Response({
        "repositories": repositories,
        "total_count": len(repositories)
    })
