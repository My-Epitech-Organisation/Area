"""
Tests for AREA serializers.

This module tests:
- Field validation
- Action↔Reaction compatibility
- JSON configuration validation
- Serializer methods and behavior
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers

from automations.models import Service, Action, Reaction, Area
from automations.serializers import (
    ServiceSerializer,
    ActionSerializer,
    ReactionSerializer,
    AreaSerializer,
    AreaCreateSerializer,
    AboutServiceSerializer
)

User = get_user_model()


class ServiceSerializerTest(TestCase):
    """Test ServiceSerializer functionality."""

    def setUp(self):
        """Set up test data."""
        self.service = Service.objects.create(
            name="github",
            description="GitHub integration service",
            status=Service.Status.ACTIVE
        )

        # Create some actions and reactions for count testing
        Action.objects.create(
            service=self.service,
            name="new_issue",
            description="New issue created"
        )
        Reaction.objects.create(
            service=self.service,
            name="create_issue",
            description="Create a new issue"
        )

    def test_service_serialization(self):
        """Test basic service serialization."""
        serializer = ServiceSerializer(self.service)
        data = serializer.data

        self.assertEqual(data['name'], 'github')
        self.assertEqual(data['description'], 'GitHub integration service')
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['actions_count'], 1)
        self.assertEqual(data['reactions_count'], 1)

    def test_read_only_fields(self):
        """Test that all fields are read-only."""
        serializer = ServiceSerializer()
        for field_name in ['id', 'name', 'description', 'status', 'actions_count', 'reactions_count']:
            self.assertIn(field_name, serializer.Meta.read_only_fields)


class ActionReactionSerializerTest(TestCase):
    """Test ActionSerializer and ReactionSerializer."""

    def setUp(self):
        """Set up test data."""
        self.service = Service.objects.create(
            name="github",
            description="GitHub service",
            status=Service.Status.ACTIVE
        )

        self.action = Action.objects.create(
            service=self.service,
            name="new_issue",
            description="New issue created"
        )

        self.reaction = Reaction.objects.create(
            service=self.service,
            name="create_comment",
            description="Create a comment"
        )

    def test_action_serialization(self):
        """Test action serialization with service info."""
        serializer = ActionSerializer(self.action)
        data = serializer.data

        self.assertEqual(data['name'], 'new_issue')
        self.assertEqual(data['description'], 'New issue created')
        self.assertEqual(data['service_name'], 'github')
        self.assertEqual(data['service_id'], self.service.id)

    def test_reaction_serialization(self):
        """Test reaction serialization with service info."""
        serializer = ReactionSerializer(self.reaction)
        data = serializer.data

        self.assertEqual(data['name'], 'create_comment')
        self.assertEqual(data['description'], 'Create a comment')
        self.assertEqual(data['service_name'], 'github')
        self.assertEqual(data['service_id'], self.service.id)


class AreaSerializerTest(TestCase):
    """Test AreaSerializer and AreaCreateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.service = Service.objects.create(
            name="github",
            description="GitHub service",
            status=Service.Status.ACTIVE
        )

        self.action = Action.objects.create(
            service=self.service,
            name="timer_daily",
            description="Daily timer trigger"
        )

        self.reaction = Reaction.objects.create(
            service=self.service,
            name="send_email",
            description="Send email notification"
        )

        self.area = Area.objects.create(
            owner=self.user,
            name="Daily Email Report",
            action=self.action,
            reaction=self.reaction,
            action_config={"hour": 9, "minute": 0, "timezone": "UTC"},
            reaction_config={"recipient": "user@example.com", "subject": "Daily Report"},
            status=Area.Status.ACTIVE
        )

    def test_area_serialization(self):
        """Test basic area serialization."""
        serializer = AreaSerializer(self.area)
        data = serializer.data

        self.assertEqual(data['name'], 'Daily Email Report')
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['action_name'], 'timer_daily')
        self.assertEqual(data['reaction_name'], 'send_email')
        self.assertEqual(data['action_service'], 'github')
        self.assertEqual(data['reaction_service'], 'github')
        self.assertIn('created_at', data)

    def test_area_create_serializer_validation(self):
        """Test AreaCreateSerializer validation."""
        valid_data = {
            'name': 'Test Area',
            'action': self.action.id,
            'reaction': self.reaction.id,
            'action_config': {"hour": 10, "minute": 30, "timezone": "UTC"},
            'reaction_config': {"recipient": "test@example.com", "subject": "Test"}
        }

        serializer = AreaCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), f"Errors: {serializer.errors}")

    def test_area_create_invalid_action_config(self):
        """Test validation of invalid action_config."""
        invalid_data = {
            'name': 'Test Area',
            'action': self.action.id,
            'reaction': self.reaction.id,
            'action_config': {"hour": 25, "minute": 30},  # Invalid hour
            'reaction_config': {"recipient": "test@example.com", "subject": "Test"}
        }

        serializer = AreaCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('action_config', serializer.errors)

    def test_area_create_invalid_reaction_config(self):
        """Test validation of invalid reaction_config."""
        invalid_data = {
            'name': 'Test Area',
            'action': self.action.id,
            'reaction': self.reaction.id,
            'action_config': {"hour": 10, "minute": 30, "timezone": "UTC"},
            'reaction_config': {"recipient": "not-an-email", "subject": "Test"}  # Invalid email
        }

        serializer = AreaCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reaction_config', serializer.errors)


class CompatibilityValidationTest(TestCase):
    """Test action↔reaction compatibility validation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # GitHub service with actions and reactions
        self.github_service = Service.objects.create(
            name="github",
            description="GitHub service",
            status=Service.Status.ACTIVE
        )

        self.github_action = Action.objects.create(
            service=self.github_service,
            name="github_new_issue",
            description="New GitHub issue"
        )

        self.github_reaction = Reaction.objects.create(
            service=self.github_service,
            name="github_create_issue",
            description="Create GitHub issue"
        )

        # Email service
        self.email_service = Service.objects.create(
            name="email",
            description="Email service",
            status=Service.Status.ACTIVE
        )

        self.email_reaction = Reaction.objects.create(
            service=self.email_service,
            name="send_email",
            description="Send email"
        )

    def test_incompatible_github_to_github(self):
        """Test that GitHub action to GitHub reaction is blocked."""
        invalid_data = {
            'name': 'Invalid Area',
            'action': self.github_action.id,
            'reaction': self.github_reaction.id,  # Same service = incompatible
            'action_config': {"repository": "user/repo"},
            'reaction_config': {"repository": "user/other-repo", "title": "New issue"}
        }

        serializer = AreaCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        # Should have compatibility error
        self.assertTrue(any('compatible' in str(error).lower() for error in serializer.errors.values()))

    def test_compatible_github_to_email(self):
        """Test that GitHub action to email reaction is allowed."""
        valid_data = {
            'name': 'Valid Area',
            'action': self.github_action.id,
            'reaction': self.email_reaction.id,  # Different service = compatible
            'action_config': {"repository": "user/repo"},
            'reaction_config': {"recipient": "user@example.com", "subject": "GitHub alert"}
        }

        serializer = AreaCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), f"Errors: {serializer.errors}")


class AboutServiceSerializerTest(TestCase):
    """Test AboutServiceSerializer for /about.json endpoint."""

    def setUp(self):
        """Set up test data."""
        self.service = Service.objects.create(
            name="github",
            description="GitHub service",
            status=Service.Status.ACTIVE
        )

        self.action = Action.objects.create(
            service=self.service,
            name="new_issue",
            description="New issue created"
        )

        self.reaction = Reaction.objects.create(
            service=self.service,
            name="create_comment",
            description="Create comment"
        )

    def test_about_service_serialization(self):
        """Test AboutServiceSerializer includes nested actions/reactions."""
        serializer = AboutServiceSerializer(self.service)
        data = serializer.data

        self.assertEqual(data['name'], 'github')
        self.assertIn('actions', data)
        self.assertIn('reactions', data)
        self.assertEqual(len(data['actions']), 1)
        self.assertEqual(len(data['reactions']), 1)
        self.assertEqual(data['actions'][0]['name'], 'new_issue')
        self.assertEqual(data['reactions'][0]['name'], 'create_comment')


class ConfigurationValidationTest(TestCase):
    """Test JSON configuration validation in detail."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.service = Service.objects.create(
            name="test_service",
            description="Test service",
            status=Service.Status.ACTIVE
        )

        self.timer_action = Action.objects.create(
            service=self.service,
            name="timer_daily",
            description="Daily timer"
        )

        self.email_reaction = Reaction.objects.create(
            service=self.service,
            name="send_email",
            description="Send email"
        )

    def test_timer_daily_valid_configs(self):
        """Test various valid timer_daily configurations."""
        valid_configs = [
            {"hour": 0, "minute": 0, "timezone": "UTC"},
            {"hour": 23, "minute": 59, "timezone": "America/New_York"},
            {"hour": 12, "minute": 30, "timezone": "Europe/Paris"}
        ]

        for config in valid_configs:
            data = {
                'name': 'Test Timer',
                'action': self.timer_action.id,
                'reaction': self.email_reaction.id,
                'action_config': config,
                'reaction_config': {"recipient": "test@example.com", "subject": "Test"}
            }

            serializer = AreaCreateSerializer(data=data)
            self.assertTrue(serializer.is_valid(),
                          f"Config {config} should be valid. Errors: {serializer.errors}")

    def test_timer_daily_invalid_configs(self):
        """Test various invalid timer_daily configurations."""
        invalid_configs = [
            {"hour": 24, "minute": 0, "timezone": "UTC"},  # Hour too high
            {"hour": -1, "minute": 0, "timezone": "UTC"},  # Hour too low
            {"hour": 12, "minute": 60, "timezone": "UTC"},  # Minute too high
            {"hour": 12, "minute": -1, "timezone": "UTC"},  # Minute too low
            {"hour": 12},  # Missing required fields
            {}  # Empty config
        ]

        for config in invalid_configs:
            data = {
                'name': 'Test Timer',
                'action': self.timer_action.id,
                'reaction': self.email_reaction.id,
                'action_config': config,
                'reaction_config': {"recipient": "test@example.com", "subject": "Test"}
            }

            serializer = AreaCreateSerializer(data=data)
            self.assertFalse(serializer.is_valid(),
                           f"Config {config} should be invalid but passed validation")

    def test_email_valid_configs(self):
        """Test various valid email configurations."""
        valid_configs = [
            {"recipient": "user@example.com", "subject": "Test"},
            {"recipient": "test.user+tag@domain.co.uk", "subject": "Long subject", "body": "Email body"},
            {"recipient": "admin@localhost.localdomain", "subject": "Local", "template_vars": {"name": "John"}}
        ]

        for config in valid_configs:
            data = {
                'name': 'Test Email',
                'action': self.timer_action.id,
                'reaction': self.email_reaction.id,
                'action_config': {"hour": 12, "minute": 0, "timezone": "UTC"},
                'reaction_config': config
            }

            serializer = AreaCreateSerializer(data=data)
            self.assertTrue(serializer.is_valid(),
                          f"Config {config} should be valid. Errors: {serializer.errors}")

    def test_email_invalid_configs(self):
        """Test various invalid email configurations."""
        invalid_configs = [
            {"recipient": "not-an-email", "subject": "Test"},  # Invalid email
            {"recipient": "user@example.com"},  # Missing subject
            {"recipient": "", "subject": "Test"},  # Empty email
            {"recipient": "user@example.com", "subject": ""},  # Empty subject
            {}  # Empty config
        ]

        for config in invalid_configs:
            data = {
                'name': 'Test Email',
                'action': self.timer_action.id,
                'reaction': self.email_reaction.id,
                'action_config': {"hour": 12, "minute": 0, "timezone": "UTC"},
                'reaction_config': config
            }

            serializer = AreaCreateSerializer(data=data)
            self.assertFalse(serializer.is_valid(),
                           f"Config {config} should be invalid but passed validation")