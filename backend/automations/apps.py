from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "automations"

    def ready(self):
        """
        Import signals when Django starts.
        This ensures our webhook auto-management signals are registered.
        """
        import automations.signals  # noqa: F401
