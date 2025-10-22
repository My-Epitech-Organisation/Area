import os
import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "area_project.settings")

app = Celery("area_project")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("area_project.settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# =============================================================================
# CELERY BEAT SCHEDULE - Periodic Tasks
# =============================================================================
app.conf.beat_schedule = {
    "check-timer-actions": {
        "task": "automations.check_timer_actions",
        "schedule": 60.0,  # Every minute
    },
    "check-github-actions": {
        "task": "automations.check_github_actions",
        "schedule": 300.0,  # Every 5 minutes (GitHub polling - webhooks preferred)
    },
    "check-gmail-actions": {
        "task": "automations.check_gmail_actions",
        "schedule": 180.0,  # Every 3 minutes
    },
    "check-twitch-actions": {
        "task": "automations.check_twitch_actions",
        "schedule": 60.0,  # Every minute
    },
    "collect-execution-metrics": {
        "task": "automations.collect_execution_metrics",
        "schedule": crontab(minute=0),  # Every hour
    },
    "cleanup-old-executions": {
        "task": "automations.cleanup_old_executions",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
