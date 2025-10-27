"""
Tests for AREA API views.

This module tests:
- CRUD operations for Areas
- Permissions and ownership
- Pagination and filtering
- About.json endpoint
- ViewSet behavior
"""

import json
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from automations.models import Action, Area, Reaction, Service
from automations.views import about_json_view

User = get_user_model()


class BaseAPITest(APITestCase):
    """Base class for API tests with common setup."""

    def setUp(self):
        """Set up test data for API tests."""
        # Create test users with verified emails
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user1.email_verified = True
        self.user1.save()

        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.user2.email_verified = True
        self.user2.save()

        # Create test services
        self.github_service = Service.objects.create(
            name="github",
            description="GitHub integration",
            status=Service.Status.ACTIVE,
        )

        self.email_service = Service.objects.create(
            name="email", description="Email service", status=Service.Status.ACTIVE
        )

        self.timer_service = Service.objects.create(
            name="timer", description="Timer service", status=Service.Status.ACTIVE
        )

        # Create test actions
        self.timer_action = Action.objects.create(
            service=self.timer_service,
            name="timer_daily",
            description="Daily timer trigger",
        )

        self.github_action = Action.objects.create(
            service=self.github_service,
            name="github_new_issue",
            description="New GitHub issue",
        )

        # Create test reactions
        self.email_reaction = Reaction.objects.create(
            service=self.email_service,
            name="send_email",
            description="Send email notification",
        )

        self.slack_reaction = Reaction.objects.create(
            service=self.github_service,
            name="slack_message",
            description="Send Slack message",
        )

        # Create test areas
        self.area1 = Area.objects.create(
            owner=self.user1,
            name="User1 Area 1",
            action=self.timer_action,
            reaction=self.email_reaction,
            action_config={"hour": 9, "minute": 0, "timezone": "UTC"},
            reaction_config={
                "recipient": "user1@example.com",
                "subject": "Daily Report",
            },
            status=Area.Status.ACTIVE,
        )

        self.area2 = Area.objects.create(
            owner=self.user2,
            name="User2 Area 1",
            action=self.github_action,
            reaction=self.slack_reaction,
            action_config={"repository": "user2/repo"},
            reaction_config={"channel": "#alerts", "message": "New issue!"},
            status=Area.Status.DISABLED,
        )

        # Setup API client
        self.client = APIClient()

    def authenticate_user(self, user):
        """Authenticate a user for API requests."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def get_url(self, viewname, *args, **kwargs):
        """Helper to get URL for API endpoints."""
        return reverse(f"automations:{viewname}", *args, **kwargs)


class ServiceViewSetTest(BaseAPITest):
    """Test ServiceViewSet (read-only)."""

    def test_list_services_authenticated(self):
        """Test listing services when authenticated."""
        self.authenticate_user(self.user1)
        url = self.get_url("service-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should return both active services
        data = response.json()
        self.assertEqual(len(data["results"]), 3)
        service_names = [s["name"] for s in data["results"]]
        self.assertIn("github", service_names)
        self.assertIn("email", service_names)
        self.assertIn("timer", service_names)

    def test_list_services_unauthenticated(self):
        """Test that unauthenticated requests are rejected."""
        url = self.get_url("service-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_service(self):
        """Test retrieving a single service."""
        self.authenticate_user(self.user1)
        url = self.get_url("service-detail", kwargs={"pk": self.github_service.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["name"], "github")
        self.assertEqual(data["actions_count"], 1)  # github_new_issue
        self.assertEqual(data["reactions_count"], 1)  # slack_message

    def test_service_viewset_read_only(self):
        """Test that service endpoints are read-only."""
        self.authenticate_user(self.user1)
        url = self.get_url("service-list")

        # POST should not be allowed
        response = self.client.post(url, {"name": "test"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT should not be allowed
        url = self.get_url("service-detail", kwargs={"pk": self.github_service.id})
        response = self.client.put(url, {"name": "updated"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ActionReactionViewSetTest(BaseAPITest):
    """Test ActionViewSet and ReactionViewSet (read-only)."""

    def test_list_actions(self):
        """Test listing actions."""
        self.authenticate_user(self.user1)
        url = self.get_url("action-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        action_names = [a["name"] for a in data["results"]]
        self.assertIn("timer_daily", action_names)
        self.assertIn("github_new_issue", action_names)

    def test_list_reactions(self):
        """Test listing reactions."""
        self.authenticate_user(self.user1)
        url = self.get_url("reaction-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 2)
        reaction_names = [r["name"] for r in data["results"]]
        self.assertIn("send_email", reaction_names)
        self.assertIn("slack_message", reaction_names)

    def test_filter_actions_by_service(self):
        """Test filtering actions by service."""
        self.authenticate_user(self.user1)
        url = self.get_url("action-list")

        response = self.client.get(url, {"service": self.github_service.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        # Only github_new_issue belongs to github service now
        self.assertEqual(len(data["results"]), 1)

        for action in data["results"]:
            self.assertEqual(action["service_name"], "github")


class AreaViewSetTest(BaseAPITest):
    """Test AreaViewSet CRUD operations."""

    def test_list_areas_ownership(self):
        """Test that users only see their own areas."""
        # User1 should only see their area
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "User1 Area 1")

        # User2 should only see their area
        self.authenticate_user(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "User2 Area 1")

    def test_create_area_valid(self):
        """Test creating a valid area."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        data = {
            "name": "New Test Area",
            "action": self.timer_action.id,
            "reaction": self.email_reaction.id,
            "action_config": {"hour": 14, "minute": 30, "timezone": "UTC"},
            "reaction_config": {
                "recipient": "test@example.com",
                "subject": "Test Alert",
            },
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify area was created
        area = Area.objects.get(name="New Test Area")
        self.assertEqual(area.owner, self.user1)
        self.assertEqual(area.action, self.timer_action)
        self.assertEqual(area.reaction, self.email_reaction)

    def test_create_area_invalid_config(self):
        """Test creating area with invalid configuration."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        data = {
            "name": "Invalid Area",
            "action": self.timer_action.id,
            "reaction": self.email_reaction.id,
            "action_config": {"hour": 25, "minute": 30},  # Invalid hour
            "reaction_config": {"recipient": "test@example.com", "subject": "Test"},
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("action_config", response.json())

    def test_update_own_area(self):
        """Test updating own area."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-detail", kwargs={"pk": self.area1.id})

        data = {
            "name": "Updated Area Name",
            "action": self.area1.action.id,
            "reaction": self.area1.reaction.id,
            "action_config": self.area1.action_config,
            "reaction_config": self.area1.reaction_config,
            "status": "disabled",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify update
        self.area1.refresh_from_db()
        self.assertEqual(self.area1.name, "Updated Area Name")
        self.assertEqual(self.area1.status, Area.Status.DISABLED)

    def test_cannot_update_others_area(self):
        """Test that users cannot update other users' areas."""
        self.authenticate_user(self.user1)
        url = self.get_url(
            "area-detail", kwargs={"pk": self.area2.id}
        )  # area2 belongs to user2

        data = {"name": "Hacked Area"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify area was not changed
        self.area2.refresh_from_db()
        self.assertEqual(self.area2.name, "User2 Area 1")

    def test_delete_own_area(self):
        """Test deleting own area."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-detail", kwargs={"pk": self.area1.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify area was deleted
        self.assertFalse(Area.objects.filter(id=self.area1.id).exists())

    def test_cannot_delete_others_area(self):
        """Test that users cannot delete other users' areas."""
        self.authenticate_user(self.user1)
        url = self.get_url(
            "area-detail", kwargs={"pk": self.area2.id}
        )  # area2 belongs to user2

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify area was not deleted
        self.assertTrue(Area.objects.filter(id=self.area2.id).exists())


class AreaCustomActionsTest(BaseAPITest):
    """Test custom actions on AreaViewSet."""

    def test_toggle_status_action(self):
        """Test toggle_status custom action."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-toggle-status", kwargs={"pk": self.area1.id})

        # Area starts as ACTIVE
        self.assertEqual(self.area1.status, Area.Status.ACTIVE)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should now be DISABLED
        self.area1.refresh_from_db()
        self.assertEqual(self.area1.status, Area.Status.DISABLED)

        # Toggle again
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should be ACTIVE again
        self.area1.refresh_from_db()
        self.assertEqual(self.area1.status, Area.Status.ACTIVE)

    def test_pause_resume_actions(self):
        """Test pause and resume custom actions."""
        self.authenticate_user(self.user1)

        # Test pause
        pause_url = self.get_url("area-pause", kwargs={"pk": self.area1.id})
        response = self.client.post(pause_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.area1.refresh_from_db()
        self.assertEqual(self.area1.status, Area.Status.PAUSED)

        # Test resume
        resume_url = self.get_url("area-resume", kwargs={"pk": self.area1.id})
        response = self.client.post(resume_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.area1.refresh_from_db()
        self.assertEqual(self.area1.status, Area.Status.ACTIVE)

    def test_stats_action(self):
        """Test stats custom action."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-stats")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["active"], 1)
        self.assertEqual(data["disabled"], 0)
        self.assertEqual(data["paused"], 0)
        self.assertIn("by_service", data)


class PaginationFilteringTest(BaseAPITest):
    """Test pagination and filtering functionality."""

    def setUp(self):
        """Set up additional test data for pagination tests."""
        super().setUp()

        # Create more areas for pagination testing
        for i in range(25):  # More than default page size
            Area.objects.create(
                owner=self.user1,
                name=f"Area {i+2}",  # Start from 2 since area1 already exists
                action=self.timer_action,
                reaction=self.email_reaction,
                action_config={"hour": 9, "minute": 0, "timezone": "UTC"},
                reaction_config={
                    "recipient": f"user{i}@example.com",
                    "subject": f"Report {i}",
                },
                status=Area.Status.ACTIVE if i % 2 == 0 else Area.Status.DISABLED,
            )

    def test_area_pagination(self):
        """Test that area list is paginated."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("results", data)
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)

        # Should have page_size items (default 20)
        self.assertEqual(len(data["results"]), 20)
        self.assertEqual(data["count"], 26)  # 1 original + 25 created = 26 total

    def test_area_filtering_by_status(self):
        """Test filtering areas by status."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        # Filter for active areas only
        response = self.client.get(url, {"status": "active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        # All returned areas should be active
        for area in data["results"]:
            self.assertEqual(area["status"], "active")

    def test_area_search(self):
        """Test searching areas by name."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        # Search for areas containing "User1" to be more specific
        response = self.client.get(url, {"search": "User1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        # Should find areas with "User1" in the name
        self.assertGreater(len(data["results"]), 0)
        for area in data["results"]:
            self.assertIn("User1", area["name"])

    def test_area_ordering(self):
        """Test ordering areas."""
        self.authenticate_user(self.user1)
        url = self.get_url("area-list")

        # Order by name
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        names = [area["name"] for area in data["results"]]
        self.assertEqual(names, sorted(names))


class AboutJsonEndpointTest(TestCase):
    """Test the /about.json endpoint."""

    def setUp(self):
        """Set up test data for about.json tests."""
        # Create services with actions and reactions
        self.github_service = Service.objects.create(
            name="github",
            description="GitHub integration",
            status=Service.Status.ACTIVE,
        )

        self.email_service = Service.objects.create(
            name="email", description="Email service", status=Service.Status.ACTIVE
        )

        # Inactive service (should not appear in about.json)
        self.inactive_service = Service.objects.create(
            name="inactive",
            description="Inactive service",
            status=Service.Status.INACTIVE,
        )

        # Create actions
        Action.objects.create(
            service=self.github_service,
            name="new_issue",
            description="New issue created",
        )

        Action.objects.create(
            service=self.github_service,
            name="new_pull_request",
            description="New pull request",
        )

        # Create reactions
        Reaction.objects.create(
            service=self.email_service,
            name="send_email",
            description="Send email notification",
        )

        Reaction.objects.create(
            service=self.github_service,
            name="create_comment",
            description="Create comment",
        )

    def test_about_json_endpoint_structure(self):
        """Test that about.json returns correct structure."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/about.json")
        request.META["HTTP_HOST"] = "localhost:8000"

        response = about_json_view(request)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        # Check main structure
        self.assertIn("client", data)
        self.assertIn("server", data)

        # Check client info
        self.assertEqual(data["client"]["host"], "localhost:8000")

        # Check server info
        self.assertIn("current_time", data["server"])
        self.assertIn("services", data["server"])
        self.assertIsInstance(data["server"]["current_time"], int)

    def test_about_json_services_content(self):
        """Test that about.json includes correct services."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/about.json")
        request.META["HTTP_HOST"] = "test.com"

        response = about_json_view(request)
        data = json.loads(response.content)

        services = data["server"]["services"]
        self.assertEqual(len(services), 2)  # Only active services

        service_names = [s["name"] for s in services]
        self.assertIn("github", service_names)
        self.assertIn("email", service_names)
        self.assertNotIn("inactive", service_names)

        # Check that services include actions and reactions
        github_service = next(s for s in services if s["name"] == "github")
        self.assertIn("actions", github_service)
        self.assertIn("reactions", github_service)
        self.assertEqual(len(github_service["actions"]), 2)
        self.assertEqual(len(github_service["reactions"]), 1)

        # Check action structure
        action = github_service["actions"][0]
        self.assertIn("name", action)
        self.assertIn("description", action)

    @patch("time.time")
    def test_about_json_timestamp(self, mock_time):
        """Test that about.json includes correct timestamp."""
        mock_time.return_value = 1234567890.0

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/about.json")
        request.META["HTTP_HOST"] = "test.com"

        response = about_json_view(request)
        data = json.loads(response.content)

        self.assertEqual(data["server"]["current_time"], 1234567890)


class APIEndpointIntegrationTest(BaseAPITest):
    """Integration tests for all API endpoints."""

    def test_full_workflow_create_and_manage_area(self):
        """Test complete workflow of creating and managing an area."""
        self.authenticate_user(self.user1)

        # 1. List available services
        services_url = self.get_url("service-list")
        response = self.client.get(services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        services = response.json()["results"]
        self.assertGreater(len(services), 0)

        # 2. List available actions
        actions_url = self.get_url("action-list")
        response = self.client.get(actions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actions = response.json()["results"]
        self.assertGreater(len(actions), 0)

        # 3. List available reactions
        reactions_url = self.get_url("reaction-list")
        response = self.client.get(reactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reactions = response.json()["results"]
        self.assertGreater(len(reactions), 0)

        # 4. Create an area
        areas_url = self.get_url("area-list")
        area_data = {
            "name": "Integration Test Area",
            "action": self.timer_action.id,
            "reaction": self.email_reaction.id,
            "action_config": {"hour": 15, "minute": 0, "timezone": "UTC"},
            "reaction_config": {"recipient": "integration@test.com", "subject": "Test"},
        }

        response = self.client.post(areas_url, area_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        area_id = response.json()["id"]

        # 5. Retrieve the created area
        area_detail_url = self.get_url("area-detail", kwargs={"pk": area_id})
        response = self.client.get(area_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        area = response.json()
        self.assertEqual(area["name"], "Integration Test Area")

        # 6. Toggle area status
        toggle_url = self.get_url("area-toggle-status", kwargs={"pk": area_id})
        response = self.client.post(toggle_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "disabled")

        # 7. Get user stats
        stats_url = self.get_url("area-stats")
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stats = response.json()
        self.assertEqual(stats["total"], 2)  # original area1 + new area

        # 8. Delete the area
        response = self.client.delete(area_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 9. Verify deletion
        response = self.client.get(area_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
