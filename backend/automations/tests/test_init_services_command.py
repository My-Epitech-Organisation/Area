"""
Tests for the init_services management command.

Tests ensure that the command correctly initializes the database with
the expected services, actions, and reactions.
"""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from automations.models import Action, Reaction, Service


class InitServicesCommandTest(TestCase):
    """Test suite for init_services management command."""

    def test_command_creates_services(self):
        """Test that the command creates all expected services."""
        # Initially, database should be empty
        self.assertEqual(Service.objects.count(), 0)

        # Run the command
        out = StringIO()
        call_command("init_services", stdout=out)

        # Check services were created
        self.assertGreater(Service.objects.count(), 0)

        # Verify specific services exist
        expected_services = [
            "timer",
            "github",
            "gmail",
            "email",
            "slack",
            "teams",
            "webhook",
        ]

        for service_name in expected_services:
            self.assertTrue(
                Service.objects.filter(name=service_name).exists(),
                f"Service '{service_name}' should exist",
            )

        # Check output
        output = out.getvalue()
        self.assertIn("initialization completed successfully", output.lower())

    def test_command_creates_actions(self):
        """Test that the command creates expected actions."""
        call_command("init_services", stdout=StringIO())

        # Verify specific actions exist
        expected_actions = [
            ("timer", "timer_daily"),
            ("timer", "timer_weekly"),
            ("github", "github_new_issue"),
            ("github", "github_new_pr"),
            ("gmail", "gmail_new_email"),
            ("webhook", "webhook_trigger"),
        ]

        for service_name, action_name in expected_actions:
            self.assertTrue(
                Action.objects.filter(
                    service__name=service_name, name=action_name
                ).exists(),
                f"Action '{action_name}' should exist for service '{service_name}'",
            )

    def test_command_creates_reactions(self):
        """Test that the command creates expected reactions."""
        call_command("init_services", stdout=StringIO())

        # Verify specific reactions exist
        expected_reactions = [
            ("github", "github_create_issue"),
            ("email", "send_email"),
            ("slack", "slack_message"),
            ("teams", "teams_message"),
            ("webhook", "webhook_post"),
        ]

        for service_name, reaction_name in expected_reactions:
            self.assertTrue(
                Reaction.objects.filter(
                    service__name=service_name, name=reaction_name
                ).exists(),
                f"Reaction '{reaction_name}' should exist for service '{service_name}'",
            )

    def test_command_is_idempotent(self):
        """Test that running the command multiple times doesn't create duplicates."""
        # Run command twice
        call_command("init_services", stdout=StringIO())
        first_count = Service.objects.count()

        call_command("init_services", stdout=StringIO())
        second_count = Service.objects.count()

        # Count should be the same
        self.assertEqual(
            first_count,
            second_count,
            "Running command twice should not create duplicates",
        )

    def test_command_with_reset_flag(self):
        """Test that the --reset flag deletes existing data before initializing."""
        # Create initial data
        call_command("init_services", stdout=StringIO())
        initial_count = Service.objects.count()
        self.assertGreater(initial_count, 0)

        # Create a custom service that shouldn't survive reset
        custom_service = Service.objects.create(
            name="custom_test_service",
            description="Test service",
            status=Service.Status.ACTIVE,
        )
        self.assertTrue(Service.objects.filter(pk=custom_service.pk).exists())

        # Run with reset flag
        out = StringIO()
        call_command("init_services", "--reset", stdout=out)

        # Custom service should be deleted
        self.assertFalse(Service.objects.filter(pk=custom_service.pk).exists())

        # Standard services should be recreated
        self.assertEqual(Service.objects.count(), initial_count)

        # Check output mentions reset
        output = out.getvalue()
        self.assertIn("reset", output.lower())

    def test_timer_service_has_no_reactions(self):
        """Test that Timer service has actions but no reactions."""
        call_command("init_services", stdout=StringIO())

        timer_service = Service.objects.get(name="timer")
        self.assertGreater(timer_service.actions.count(), 0)
        self.assertEqual(timer_service.reactions.count(), 0)

    def test_email_service_has_no_actions(self):
        """Test that Email service has reactions but no actions."""
        call_command("init_services", stdout=StringIO())

        email_service = Service.objects.get(name="email")
        self.assertEqual(email_service.actions.count(), 0)
        self.assertGreater(email_service.reactions.count(), 0)

    def test_all_services_are_active(self):
        """Test that all created services are active by default."""
        call_command("init_services", stdout=StringIO())

        for service in Service.objects.all():
            self.assertEqual(
                service.status,
                Service.Status.ACTIVE,
                f"Service '{service.name}' should be active",
            )

    def test_minimum_viable_product_requirements(self):
        """Test that MVP requirements are met (min 3 services, 4 actions, 4 reactions)."""
        call_command("init_services", stdout=StringIO())

        service_count = Service.objects.count()
        action_count = Action.objects.count()
        reaction_count = Reaction.objects.count()

        self.assertGreaterEqual(
            service_count, 3, "Should have at least 3 services for MVP"
        )
        self.assertGreaterEqual(
            action_count, 4, "Should have at least 4 actions for MVP"
        )
        self.assertGreaterEqual(
            reaction_count, 4, "Should have at least 4 reactions for MVP"
        )

    def test_service_descriptions_are_not_empty(self):
        """Test that all services have meaningful descriptions."""
        call_command("init_services", stdout=StringIO())

        for service in Service.objects.all():
            self.assertTrue(
                len(service.description) > 10,
                f"Service '{service.name}' should have a meaningful description",
            )

    def test_action_descriptions_are_not_empty(self):
        """Test that all actions have meaningful descriptions."""
        call_command("init_services", stdout=StringIO())

        for action in Action.objects.all():
            self.assertTrue(
                len(action.description) > 10,
                f"Action '{action.name}' should have a meaningful description",
            )

    def test_reaction_descriptions_are_not_empty(self):
        """Test that all reactions have meaningful descriptions."""
        call_command("init_services", stdout=StringIO())

        for reaction in Reaction.objects.all():
            self.assertTrue(
                len(reaction.description) > 10,
                f"Reaction '{reaction.name}' should have a meaningful description",
            )
