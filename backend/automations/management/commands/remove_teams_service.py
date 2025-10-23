"""
Django management command to remove the Teams service from the database.

This command removes the Teams service and all associated actions, reactions,
and areas that depend on it.

Usage:
    python manage.py remove_teams_service
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from automations.models import Action, Area, Reaction, Service


class Command(BaseCommand):
    """Remove Teams service from the database."""

    help = "Remove the Teams service and all associated data from the database"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  AREA - Removing Teams Service"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        try:
            with transaction.atomic():
                # Check if Teams service exists
                try:
                    teams_service = Service.objects.get(name="teams")
                except Service.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING("  ⚠ Teams service not found (already removed)")
                    )
                    return

                # Count affected objects
                actions_count = Action.objects.filter(service=teams_service).count()
                reactions_count = Reaction.objects.filter(service=teams_service).count()
                areas_count = Area.objects.filter(
                    action__service=teams_service
                ).count() + Area.objects.filter(reaction__service=teams_service).count()

                self.stdout.write(
                    self.style.WARNING(f"  Found Teams service with:")
                )
                self.stdout.write(f"    - {actions_count} actions")
                self.stdout.write(f"    - {reactions_count} reactions")
                self.stdout.write(f"    - {areas_count} affected areas")
                self.stdout.write("")

                # Delete areas first (foreign key constraint)
                if areas_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f"  → Deleting {areas_count} affected areas...")
                    )
                    Area.objects.filter(action__service=teams_service).delete()
                    Area.objects.filter(reaction__service=teams_service).delete()

                # Delete the service (will cascade to actions and reactions)
                self.stdout.write(
                    self.style.WARNING(f"  → Deleting Teams service...")
                )
                teams_service.delete()

                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS("=" * 70))
                self.stdout.write(
                    self.style.SUCCESS("✓ Teams service successfully removed!")
                )
                self.stdout.write(self.style.SUCCESS("=" * 70))
                self.stdout.write("")
                self.stdout.write(self.style.HTTP_INFO("📊 Summary:"))
                self.stdout.write(f"   • Service removed: teams")
                self.stdout.write(f"   • Actions deleted: {actions_count}")
                self.stdout.write(f"   • Reactions deleted: {reactions_count}")
                self.stdout.write(f"   • Areas affected: {areas_count}")
                self.stdout.write("")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error during removal: {e}"))
            raise
