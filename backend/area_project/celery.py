import os
import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

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


def get_beat_schedule():
    """
    Generate Celery Beat schedule based on environment.

    DEV MODE (ENVIRONMENT=local|docker):
      - Uses POLLING for GitHub, Twitch, Slack (easier to debug)
      - No webhook configuration required

    PROD MODE (ENVIRONMENT=production):
      - Uses WEBHOOKS for GitHub, Twitch, Slack (real-time, efficient)
      - Polling tasks are automatically disabled if webhooks are configured
      - Falls back to polling if webhooks not configured
    """
    environment = getattr(settings, "ENVIRONMENT", "local")
    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})

    # Determine if we're in development mode (local or docker)
    is_dev = environment in ("local", "docker", "development")

    # Base schedule (always active)
    schedule = {
        "check-timer-actions": {
            "task": "automations.check_timer_actions",
            "schedule": 60.0,  # Every minute
        },
        "check-gmail-actions": {
            "task": "automations.check_gmail_actions",
            "schedule": 180.0,  # Every 3 minutes (no webhook support yet)
        },
        "check-google-calendar-actions": {
            "task": "automations.check_google_calendar_actions",
            "schedule": 180.0,  # Every 3 minutes (no webhook support)
        },
        "check-youtube-actions": {
            "task": "automations.check_youtube_actions",
            "schedule": 300.0,  # Every 5 minutes (polling + webhook support)
        },
        "check-weather-actions": {
            "task": "automations.check_weather_actions",
            "schedule": 300.0,  # Every 5 minutes (no webhook support)
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

    # DEV MODE: Always enable polling for easier debugging
    if is_dev:
        schedule.update(
            {
                "check-github-actions": {
                    "task": "automations.check_github_actions",
                    "schedule": 300.0,  # Every 5 minutes
                },
                "check-twitch-actions": {
                    "task": "automations.check_twitch_actions",
                    "schedule": 60.0,  # Every minute
                },
                "check-slack-actions": {
                    "task": "automations.check_slack_actions",
                    "schedule": 120.0,  # Every 2 minutes
                },
                "check-notion-actions": {
                    "task": "automations.check_notion_actions",
                    "schedule": 300.0,  # Every 5 minutes
                },
            }
        )
        print(
            f"🔧 [CELERY BEAT] DEV MODE ({environment}): Polling enabled for GitHub, Twitch, Slack, Notion"
        )

    # PROD MODE: Only enable polling if webhooks are NOT configured
    else:
        if not webhook_secrets.get("github"):
            schedule["check-github-actions"] = {
                "task": "automations.check_github_actions",
                "schedule": 300.0,  # Every 5 minutes
            }
            print(
                "⚠️  [CELERY BEAT] PROD: GitHub polling enabled (webhook not configured)"
            )
        else:
            print("✅ [CELERY BEAT] PROD: GitHub webhooks active, polling disabled")

        if not webhook_secrets.get("twitch"):
            schedule["check-twitch-actions"] = {
                "task": "automations.check_twitch_actions",
                "schedule": 60.0,  # Every minute
            }
            print(
                "⚠️  [CELERY BEAT] PROD: Twitch polling enabled (webhook not configured)"
            )
        else:
            print("✅ [CELERY BEAT] PROD: Twitch webhooks active, polling disabled")

        if not webhook_secrets.get("slack"):
            schedule["check-slack-actions"] = {
                "task": "automations.check_slack_actions",
                "schedule": 120.0,  # Every 2 minutes
            }
            print(
                "⚠️  [CELERY BEAT] PROD: Slack polling enabled (webhook not configured)"
            )
        else:
            print("✅ [CELERY BEAT] PROD: Slack webhooks active, polling disabled")

        # Notion: Always use polling (webhooks not supported)
        schedule["check-notion-actions"] = {
            "task": "automations.tasks.check_notion_actions",
            "schedule": 300.0,  # Every 5 minutes
        }
        print("✅ [CELERY BEAT] Notion polling enabled (every 5 minutes)")

    return schedule


# Apply the schedule
app.conf.beat_schedule = get_beat_schedule()
app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
