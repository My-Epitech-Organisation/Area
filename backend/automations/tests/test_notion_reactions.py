"""
Tests for Notion reaction execution.
Tests Notion reactions through _execute_reaction_logic.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class NotionReactionTests(TestCase):
    """Test Notion reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create Notion service
        self.notion_service = Service.objects.create(
            name="notion", description="Notion Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.notion_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.notion_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test Notion Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_notion_create_page_success(self, mock_post, mock_get_token):
        """Test successful Notion page creation."""
        mock_get_token.return_value = "test_notion_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "page_123",
            "url": "https://notion.so/page_123",
        }
        mock_post.return_value = mock_response

        result = _execute_reaction_logic(
            reaction_name="notion_create_page",
            reaction_config={
                "title": "Test Page",
                "content": "Test content",
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertTrue(result["success"])
        self.assertEqual(result["title"], "Test Page")
        self.assertEqual(result["page_id"], "page_123")
        self.assertIn("notion.so", result["page_url"])

        # Verify API was called correctly
        mock_get_token.assert_called_once_with(self.user, "notion")
        mock_post.assert_called_once()

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_notion_create_page_no_token(self, mock_get_token):
        """Test notion_create_page when user has no Notion token."""
        mock_get_token.return_value = None

        with self.assertRaisesMessage(ValueError, "No valid Notion token"):
            _execute_reaction_logic(
                reaction_name="notion_create_page",
                reaction_config={"title": "Test"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_notion_create_page_with_parent(self, mock_post, mock_get_token):
        """Test notion_create_page with parent page."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "page_123",
            "url": "https://notion.so/page_123",
        }
        mock_post.return_value = mock_response

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = "parent_uuid_123"

            result = _execute_reaction_logic(
                reaction_name="notion_create_page",
                reaction_config={
                    "parent_id": "https://notion.so/parent_page",
                    "title": "Child Page",
                },
                trigger_data={},
                area=self.area,
            )

            self.assertTrue(result["success"])

            # Verify parent_id was processed
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            self.assertEqual(payload["parent"]["page_id"], "parent_uuid_123")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_notion_create_page_api_error(self, mock_post, mock_get_token):
        """Test notion_create_page when API fails."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request"
        mock_post.return_value = mock_response

        with self.assertRaisesMessage(ValueError, "Notion API error"):
            _execute_reaction_logic(
                reaction_name="notion_create_page",
                reaction_config={"title": "Test"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.patch")
    def test_notion_update_page_success(self, mock_patch, mock_get_token):
        """Test successful Notion page update."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = "page_uuid_123"

            result = _execute_reaction_logic(
                reaction_name="notion_update_page",
                reaction_config={
                    "page_id": "page_uuid_123",
                    "title": "Updated Title",
                    "content": "New content",
                },
                trigger_data={},
                area=self.area,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["page_id"], "page_uuid_123")
            self.assertTrue(result["content_appended"])

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_notion_update_page_missing_page_id(self, mock_get_token):
        """Test notion_update_page with missing page_id."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "page_id is required for notion_update_page"
        ):
            _execute_reaction_logic(
                reaction_name="notion_update_page",
                reaction_config={"title": "Updated"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.notion_helper.find_notion_page_by_name")
    def test_notion_update_page_by_name(self, mock_find_page, mock_get_token):
        """Test notion_update_page finding page by name."""
        mock_get_token.return_value = "test_token"
        mock_find_page.return_value = "found_page_uuid"

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = None  # Simulate URL extraction failing

            with patch("automations.tasks.requests.patch") as mock_patch:
                mock_patch.return_value = MagicMock(status_code=200)

                result = _execute_reaction_logic(
                    reaction_name="notion_update_page",
                    reaction_config={
                        "page_id": "My Page Name",
                        "title": "Updated",
                    },
                    trigger_data={},
                    area=self.area,
                )

                self.assertTrue(result["success"])
                mock_find_page.assert_called_once_with("test_token", "My Page Name")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_notion_create_database_item_success(self, mock_post, mock_get_token):
        """Test successful Notion database item creation."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "item_123",
            "url": "https://notion.so/item_123",
        }
        mock_post.return_value = mock_response

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = "database_uuid_123"

            result = _execute_reaction_logic(
                reaction_name="notion_create_database_item",
                reaction_config={
                    "database_id": "database_uuid_123",
                    "item_name": "New Item",
                    "properties": {"Status": "Active"},
                },
                trigger_data={},
                area=self.area,
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["item_name"], "New Item")
            self.assertEqual(result["database_id"], "database_uuid_123")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_notion_create_database_item_missing_database_id(self, mock_get_token):
        """Test notion_create_database_item with missing database_id."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "database_id is required for notion_create_database_item"
        ):
            _execute_reaction_logic(
                reaction_name="notion_create_database_item",
                reaction_config={"item_name": "Test"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_notion_create_database_item_missing_item_name(self, mock_get_token):
        """Test notion_create_database_item with missing item_name."""
        mock_get_token.return_value = "test_token"

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = "db_uuid"

            with self.assertRaisesMessage(
                ValueError, "item_name is required for notion_create_database_item"
            ):
                _execute_reaction_logic(
                    reaction_name="notion_create_database_item",
                    reaction_config={
                        "database_id": "db_uuid",
                        "item_name": "",  # Empty name
                    },
                    trigger_data={},
                    area=self.area,
                )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.tasks.requests.post")
    def test_notion_create_database_item_with_json_properties(
        self, mock_post, mock_get_token
    ):
        """Test notion_create_database_item with JSON string properties."""
        mock_get_token.return_value = "test_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "item_123",
            "url": "https://notion.so/item_123",
        }
        mock_post.return_value = mock_response

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = "db_uuid"

            result = _execute_reaction_logic(
                reaction_name="notion_create_database_item",
                reaction_config={
                    "database_id": "db_uuid",
                    "item_name": "Test",
                    "properties": '{"Priority": "High"}',  # JSON string
                },
                trigger_data={},
                area=self.area,
            )

            self.assertTrue(result["success"])

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.notion_helper.find_notion_database_by_name")
    @patch("automations.tasks.requests.post")
    def test_notion_create_database_item_by_name(
        self, mock_post, mock_find_db, mock_get_token
    ):
        """Test notion_create_database_item finding database by name."""
        mock_get_token.return_value = "test_token"
        mock_find_db.return_value = "found_db_uuid"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "item_123",
            "url": "https://notion.so/item_123",
        }
        mock_post.return_value = mock_response

        with patch("automations.helpers.notion_helper.extract_notion_uuid") as mock_extract:
            mock_extract.return_value = None  # Simulate UUID extraction failing

            result = _execute_reaction_logic(
                reaction_name="notion_create_database_item",
                reaction_config={
                    "database_id": "My Database",
                    "item_name": "New Item",
                },
                trigger_data={},
                area=self.area,
            )

            self.assertTrue(result["success"])
            mock_find_db.assert_called_once_with("test_token", "My Database")
