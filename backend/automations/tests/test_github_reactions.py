"""
Tests for GitHub reaction execution.
Tests GitHub reactions through _execute_reaction_logic.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class GitHubReactionTests(TestCase):
    """Test GitHub reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create GitHub service
        self.github_service = Service.objects.create(
            name="github", description="GitHub Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.github_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.github_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test GitHub Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_success(self, mock_post, mock_get_token):
        """Test successful GitHub issue creation."""
        mock_get_token.return_value = "test_github_token"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 42,
            "html_url": "https://github.com/owner/repo/issues/42",
        }
        mock_post.return_value = mock_response

        result = _execute_reaction_logic(
            reaction_name="github_create_issue",
            reaction_config={
                "repository": "owner/repo",
                "title": "Test Issue",
                "body": "Test issue body",
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["issue_number"], 42)
        self.assertEqual(result["repository"], "owner/repo")
        self.assertIn("github.com/owner/repo/issues/42", result["issue_url"])

        # Verify API was called correctly
        mock_get_token.assert_called_once_with(self.user, "github")
        mock_post.assert_called_once()

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_github_create_issue_missing_config(self, mock_get_token):
        """Test github_create_issue with missing repository."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Repository is required for github_create_issue"
        ):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "title": "Test Issue",
                    "body": "Test body",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_github_create_issue_no_token(self, mock_get_token):
        """Test github_create_issue when user has no GitHub token."""
        mock_get_token.return_value = None

        with self.assertRaisesMessage(ValueError, "No valid GitHub token"):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "repository": "owner/repo",
                    "title": "Test Issue",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_invalid_token(self, mock_post, mock_get_token):
        """Test github_create_issue with invalid/expired token."""
        mock_get_token.return_value = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Bad credentials"
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(ValueError, "GitHub authentication failed"):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "repository": "owner/repo",
                    "title": "Test Issue",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_repo_not_found(self, mock_post, mock_get_token):
        """Test github_create_issue with non-existent repository."""
        mock_get_token.return_value = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError, "Repository owner/repo not found or no access"
        ):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "repository": "owner/repo",
                    "title": "Test Issue",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_rate_limit(self, mock_post, mock_get_token):
        """Test github_create_issue when rate limit is exceeded."""
        mock_get_token.return_value = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(
            ValueError, "GitHub API rate limit exceeded or access forbidden"
        ):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "repository": "owner/repo",
                    "title": "Test Issue",
                },
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_with_labels(self, mock_post, mock_get_token):
        """Test github_create_issue with labels."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 42,
            "html_url": "https://github.com/owner/repo/issues/42",
        }
        mock_post.return_value = mock_response

        result = _execute_reaction_logic(
            reaction_name="github_create_issue",
            reaction_config={
                "repository": "owner/repo",
                "title": "Test Issue",
                "body": "Test body",
                "labels": ["bug", "urgent"],
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])

        # Verify labels were included in API call
        call_args = mock_post.call_args
        self.assertIn("labels", call_args[1]["json"])
        self.assertEqual(call_args[1]["json"]["labels"], ["bug", "urgent"])

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_with_assignees(self, mock_post, mock_get_token):
        """Test github_create_issue with assignees."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 42,
            "html_url": "https://github.com/owner/repo/issues/42",
        }
        mock_post.return_value = mock_response

        result = _execute_reaction_logic(
            reaction_name="github_create_issue",
            reaction_config={
                "repository": "owner/repo",
                "title": "Test Issue",
                "body": "Test body",
                "assignees": ["testuser"],
            },
            trigger_data={},
            area=self.area,
        )

        self.assertTrue(result["success"])

        # Verify assignees were included in API call
        call_args = mock_post.call_args
        self.assertIn("assignees", call_args[1]["json"])
        self.assertEqual(call_args[1]["json"]["assignees"], ["testuser"])

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_github_create_issue_timeout(self, mock_post, mock_get_token):
        """Test github_create_issue when API times out."""
        mock_get_token.return_value = "test_token"

        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaisesMessage(ValueError, "GitHub API request timed out"):
            _execute_reaction_logic(
                reaction_name="github_create_issue",
                reaction_config={
                    "repository": "owner/repo",
                    "title": "Test Issue",
                },
                trigger_data={},
                area=self.area,
            )
