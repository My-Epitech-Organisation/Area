"""
Celery tasks for AREA automation execution.

This module contains the core tasks for:
- Polling timer-based actions (check_timer_actions)
- Polling external service actions (check_github_actions, check_gmail_actions)
- Executing reactions (execute_reaction)

All tasks implement idempotency using Execution.external_event_id.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Action, Area, Execution, Reaction

logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================


def create_execution_safe(
    area: Area, external_event_id: str, trigger_data: dict
) -> tuple[Optional[Execution], bool]:
    """
    Safely create an Execution with idempotency.

    Args:
        area: The Area to execute
        external_event_id: Unique event identifier
        trigger_data: Data from the trigger event

    Returns:
        tuple: (Execution instance or None, was_created boolean)
               Returns (None, False) if duplicate detected
    """
    try:
        execution, created = Execution.objects.get_or_create(
            area=area,
            external_event_id=external_event_id,
            defaults={
                "status": Execution.Status.PENDING,
                "trigger_data": trigger_data,
            },
        )

        if not created:
            logger.debug(
                f"Execution already exists for area={area.id}, "
                f"event_id={external_event_id} (idempotency)"
            )
            return None, False

        logger.info(
            f"Created execution #{execution.pk} for area '{area.name}' "
            f"(event: {external_event_id})"
        )
        return execution, True

    except IntegrityError as e:
        # Race condition - another worker already created this execution
        logger.warning(
            f"IntegrityError creating execution for area={area.id}, "
            f"event_id={external_event_id}: {e}"
        )
        return None, False


def get_active_areas(action_names: list[str]) -> list[Area]:
    """
    Get all active Areas for specified action names.

    Args:
        action_names: List of action names to filter by

    Returns:
        QuerySet of active Areas with prefetched relations
    """
    return (
        Area.objects.filter(
            action__name__in=action_names, status=Area.Status.ACTIVE
        )
        .select_related(
            "action",
            "reaction",
            "action__service",
            "reaction__service",
            "owner",
        )
        .all()
    )


def validate_timer_config(action_name: str, action_config: dict) -> tuple[bool, Optional[str]]:
    """
    Validate timer action configuration.

    Args:
        action_name: Name of the action (timer_daily or timer_weekly)
        action_config: Configuration dictionary

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    if not action_config:
        return False, "action_config is required for timer actions"

    # Validate hour (0-23)
    hour = action_config.get("hour")
    if hour is None:
        return False, "hour is required in action_config"
    if not isinstance(hour, int) or not (0 <= hour <= 23):
        return False, f"hour must be an integer between 0 and 23, got {hour}"

    # Validate minute (0-59)
    minute = action_config.get("minute")
    if minute is None:
        return False, "minute is required in action_config"
    if not isinstance(minute, int) or not (0 <= minute <= 59):
        return False, f"minute must be an integer between 0 and 59, got {minute}"

    # Validate day_of_week for weekly timers (0=Monday, 6=Sunday)
    if action_name == "timer_weekly":
        day_of_week = action_config.get("day_of_week")
        if day_of_week is None:
            return False, "day_of_week is required for timer_weekly"
        if not isinstance(day_of_week, int) or not (0 <= day_of_week <= 6):
            return False, f"day_of_week must be an integer between 0 and 6, got {day_of_week}"

    return True, None


def should_trigger_timer(area: Area, current_time: datetime) -> bool:
    """
    Check if a timer action should trigger at the current time.

    Args:
        area: Area with timer action
        current_time: Current datetime (timezone aware)

    Returns:
        True if timer should trigger, False otherwise
    """
    action_config = area.action_config
    action_name = area.action.name

    # Validate configuration
    is_valid, error = validate_timer_config(action_name, action_config)
    if not is_valid:
        logger.error(
            f"Invalid timer config for area '{area.name}' (#{area.id}): {error}"
        )
        return False

    if action_name == "timer_daily":
        # Check if current hour:minute matches configuration
        target_hour = action_config.get("hour", 0)
        target_minute = action_config.get("minute", 0)

        return (
            current_time.hour == target_hour and current_time.minute == target_minute
        )

    elif action_name == "timer_weekly":
        # Check day of week (0=Monday, 6=Sunday) and time
        target_day = action_config.get("day_of_week", 0)
        target_hour = action_config.get("hour", 0)
        target_minute = action_config.get("minute", 0)

        return (
            current_time.weekday() == target_day
            and current_time.hour == target_hour
            and current_time.minute == target_minute
        )

    return False


def handle_timer_action(area: Area, current_time: datetime) -> Optional[Execution]:
    """
    Handle a timer action trigger for a specific area.

    This function:
    1. Validates the timer configuration
    2. Checks if the timer should trigger now
    3. Creates an execution with idempotency
    4. Queues the reaction execution

    Args:
        area: The Area with timer action to process
        current_time: Current datetime (timezone aware)

    Returns:
        Execution instance if created, None otherwise
    """
    action_name = area.action.name

    # Validate timer configuration
    is_valid, error = validate_timer_config(action_name, area.action_config)
    if not is_valid:
        logger.error(
            f"Invalid timer config for area '{area.name}' (#{area.id}): {error}"
        )
        return None

    # Check if timer should trigger
    if not should_trigger_timer(area, current_time):
        return None

    # Create unique event ID based on time (minute precision)
    # This ensures idempotency: same minute = same event_id
    event_id = f"timer_{area.id}_{current_time.strftime('%Y%m%d%H%M')}"

    # Prepare trigger data with full context
    trigger_data = {
        "timestamp": current_time.isoformat(),
        "action_type": action_name,
        "action_config": area.action_config,
        "triggered_at": {
            "hour": current_time.hour,
            "minute": current_time.minute,
            "weekday": current_time.weekday(),
            "date": current_time.date().isoformat(),
        },
    }

    # Create execution with idempotency
    execution, created = create_execution_safe(
        area=area,
        external_event_id=event_id,
        trigger_data=trigger_data,
    )

    if created and execution:
        # Queue the reaction execution
        execute_reaction.delay(execution.pk)
        logger.info(
            f"Timer triggered for area '{area.name}' (#{area.id}): "
            f"execution #{execution.pk} queued"
        )
        return execution
    else:
        logger.debug(
            f"Timer already triggered for area '{area.name}' (#{area.id}) "
            f"at {current_time.strftime('%Y-%m-%d %H:%M')} (idempotency)"
        )
        return None


# ==================== Celery Tasks ====================


@shared_task(
    name="automations.check_timer_actions",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def check_timer_actions(self):
    """
    Check all timer-based actions and trigger executions.

    This task runs every minute via Celery Beat.
    Creates executions for timer_daily and timer_weekly actions.

    Returns:
        dict: Statistics about triggered timers
    """
    logger.info("Starting timer actions check")

    now = timezone.now()
    triggered_count = 0
    skipped_count = 0
    error_count = 0

    try:
        # Get all active areas with timer actions
        timer_areas = get_active_areas(["timer_daily", "timer_weekly"])

        logger.debug(
            f"Found {len(timer_areas)} active timer areas at "
            f"{now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

        for area in timer_areas:
            try:
                # Use the dedicated handler function
                execution = handle_timer_action(area, now)

                if execution:
                    triggered_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing timer area '{area.name}' (#{area.pk}): {e}",
                    exc_info=True,
                )
                # Continue processing other areas
                continue

        logger.info(
            f"Timer check complete: {triggered_count} triggered, "
            f"{skipped_count} skipped, {error_count} errors "
            f"(total: {len(timer_areas)} areas)"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "errors": error_count,
            "checked_areas": len(timer_areas),
            "timestamp": now.isoformat(),
        }

    except Exception as exc:
        logger.error(f"Fatal error in check_timer_actions: {exc}", exc_info=True)
        # Retry the task
        raise self.retry(exc=exc, countdown=60)


@shared_task(
    name="automations.check_github_actions",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def check_github_actions(self):
    """
    Check GitHub-based actions (polling mode).

    This task runs every 5 minutes via Celery Beat.
    Uses OAuth2 tokens to access GitHub API for each user's areas.
    For production, webhooks are preferred over polling.

    Returns:
        dict: Statistics about processed GitHub events
    """
    logger.info("Starting GitHub actions check (polling)")

    triggered_count = 0
    skipped_count = 0
    no_token_count = 0

    try:
        from users.oauth.manager import OAuthManager

        # Get all active areas with GitHub actions
        github_areas = get_active_areas(["github_new_issue", "github_new_pr"])

        logger.debug(f"Found {len(github_areas)} active GitHub areas")

        for area in github_areas:
            try:
                # Get valid OAuth2 token for the user
                access_token = OAuthManager.get_valid_token(area.owner, "github")

                if not access_token:
                    logger.warning(
                        f"Area {area.id} (user: {area.owner.username}): "
                        f"No valid GitHub token available, skipping"
                    )
                    no_token_count += 1
                    continue

                # TODO: Implement actual GitHub API polling with the token
                # Example:
                # import requests
                # headers = {"Authorization": f"Bearer {access_token}"}
                # response = requests.get("https://api.github.com/user/repos", headers=headers)
                # Check for new issues/PRs based on area.action_config

                logger.debug(
                    f"Would poll GitHub API for area {area.id} "
                    f"(action: {area.action.name})"
                )
                skipped_count += 1

            except Exception as e:
                logger.error(
                    f"Error processing GitHub area {area.id}: {e}", exc_info=True
                )
                skipped_count += 1
                continue

        logger.info(
            f"GitHub polling check completed. "
            f"Triggered: {triggered_count}, Skipped: {skipped_count}, No token: {no_token_count}"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "no_token": no_token_count,
            "checked_areas": len(github_areas),
            "note": "GitHub webhooks preferred over polling",
        }

    except Exception as exc:
        logger.error(f"Error in check_github_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300)


@shared_task(
    name="automations.execute_reaction_task",
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),  # Auto-retry on any exception
    retry_backoff=True,  # Enable exponential backoff
    retry_backoff_max=900,  # Max 15 minutes backoff
    retry_jitter=True,  # Add random jitter to prevent thundering herd
)
def execute_reaction_task(self, execution_id: int):
    """
    Execute a reaction for a given execution.

    This task is queued when an action triggers.
    It performs the actual reaction work and updates execution status.

    Retry strategy:
    - Attempt 1: Immediate
    - Attempt 2: ~60s backoff (with jitter)
    - Attempt 3: ~120s backoff (with jitter)
    - Attempt 4: ~240s backoff (with jitter, capped at 900s)

    Args:
        execution_id: ID of the Execution to process

    Returns:
        dict: Result of the execution
    """
    retry_count = self.request.retries

    try:
        # Get execution with related data
        execution = Execution.objects.select_related(
            "area", "area__action", "area__reaction", "area__owner"
        ).get(pk=execution_id)

        logger.info(
            f"Executing reaction for execution #{execution_id}, "
            f"area '{execution.area.name}' (attempt {retry_count + 1}/{self.max_retries + 1})"
        )

        # Mark execution as started
        execution.mark_started()

        # Get reaction details
        reaction_name = execution.area.reaction.name
        reaction_config = execution.area.reaction_config
        trigger_data = execution.trigger_data

        # Execute the reaction based on type
        result = _execute_reaction_logic(
            reaction_name=reaction_name,
            reaction_config=reaction_config,
            trigger_data=trigger_data,
            area=execution.area,
        )

        # Mark execution as successful
        execution.mark_success(result)

        logger.info(
            f"Successfully executed reaction for execution #{execution_id}: "
            f"{reaction_name} (after {retry_count + 1} attempt(s))"
        )

        return {
            "status": "success",
            "execution_id": execution_id,
            "reaction": reaction_name,
            "duration": execution.duration,
            "retry_count": retry_count,
        }

    except Execution.DoesNotExist:
        logger.error(f"Execution #{execution_id} not found")
        # Don't retry if execution doesn't exist
        return {"status": "error", "message": "Execution not found"}

    except Exception as exc:
        logger.error(
            f"Error executing reaction for execution #{execution_id} "
            f"(attempt {retry_count + 1}/{self.max_retries + 1}): {exc}",
            exc_info=True,
        )

        # Update execution status
        try:
            execution = Execution.objects.get(pk=execution_id)
            error_message = f"Attempt {retry_count + 1} failed: {str(exc)}"
            execution.mark_failed(error_message)
        except Execution.DoesNotExist:
            pass

        # Check if we've exhausted retries
        if retry_count >= self.max_retries:
            logger.error(
                f"Max retries ({self.max_retries}) exceeded for execution #{execution_id}. "
                f"Moving to dead letter queue."
            )

            # Send to dead letter queue
            send_to_dead_letter_queue.delay(
                execution_id=execution_id,
                error=str(exc),
                retry_count=retry_count,
            )

            return {
                "status": "failed_permanently",
                "execution_id": execution_id,
                "error": "Max retries exceeded",
                "retry_count": retry_count,
            }

        # Re-raise to trigger Celery's auto-retry with exponential backoff
        raise


# Backward compatibility: keep the old name as an alias
execute_reaction = execute_reaction_task


@shared_task(name="automations.send_to_dead_letter_queue")
def send_to_dead_letter_queue(execution_id: int, error: str, retry_count: int):
    """
    Handle permanently failed executions.

    This task is called when an execution has exhausted all retries.
    It logs the failure and could trigger notifications/alerts.

    Args:
        execution_id: ID of the failed execution
        error: Error message from the last attempt
        retry_count: Number of retries that were attempted
    """
    logger.error(
        f"[DEAD LETTER QUEUE] Execution #{execution_id} permanently failed "
        f"after {retry_count + 1} attempts. Error: {error}"
    )

    try:
        execution = Execution.objects.get(pk=execution_id)

        # Update execution with DLQ information
        dlq_message = (
            f"Moved to dead letter queue after {retry_count + 1} failed attempts. "
            f"Last error: {error}"
        )
        execution.mark_failed(dlq_message)

        # Log detailed information for monitoring
        logger.error(
            f"[DLQ Details] Area: {execution.area.name} (ID: {execution.area.pk}), "
            f"Action: {execution.area.action.name}, "
            f"Reaction: {execution.area.reaction.name}, "
            f"Owner: {execution.area.owner.email}"
        )

        # TODO: Send notification to area owner
        # TODO: Trigger alert to monitoring system (e.g., Sentry, PagerDuty)

    except Execution.DoesNotExist:
        logger.error(f"[DLQ] Execution #{execution_id} not found in database")

    return {
        "status": "dlq_processed",
        "execution_id": execution_id,
        "retry_count": retry_count,
    }


@shared_task(name="automations.collect_execution_metrics")
def collect_execution_metrics():
    """
    Collect and log execution metrics for monitoring.

    This task runs periodically (e.g., every hour) to gather statistics
    about automation executions for observability.

    Returns:
        dict: Collected metrics
    """
    from django.db.models import Count, Avg, Q
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)

    # Get metrics for last hour
    hour_metrics = Execution.objects.filter(created_at__gte=last_hour).aggregate(
        total=Count("id"),
        success=Count("id", filter=Q(status="success")),
        failed=Count("id", filter=Q(status="failed")),
        pending=Count("id", filter=Q(status="pending")),
        running=Count("id", filter=Q(status="running")),
    )

    # Get metrics for last 24 hours
    day_metrics = Execution.objects.filter(created_at__gte=last_24h).aggregate(
        total=Count("id"),
        success=Count("id", filter=Q(status="success")),
        failed=Count("id", filter=Q(status="failed")),
    )

    # Calculate success rate
    hour_success_rate = (
        (hour_metrics["success"] / hour_metrics["total"] * 100)
        if hour_metrics["total"] > 0
        else 0
    )
    day_success_rate = (
        (day_metrics["success"] / day_metrics["total"] * 100)
        if day_metrics["total"] > 0
        else 0
    )

    metrics = {
        "timestamp": now.isoformat(),
        "last_hour": {
            "total_executions": hour_metrics["total"],
            "successful": hour_metrics["success"],
            "failed": hour_metrics["failed"],
            "pending": hour_metrics["pending"],
            "running": hour_metrics["running"],
            "success_rate": round(hour_success_rate, 2),
        },
        "last_24h": {
            "total_executions": day_metrics["total"],
            "successful": day_metrics["success"],
            "failed": day_metrics["failed"],
            "success_rate": round(day_success_rate, 2),
        },
    }

    logger.info(f"[METRICS] Execution metrics: {metrics}")

    # TODO: Send metrics to monitoring system (e.g., Prometheus, CloudWatch)

    return metrics


@shared_task(name="automations.cleanup_old_executions")
def cleanup_old_executions():
    """
    Clean up old execution records to prevent database bloat.

    Retention policy:
    - Successful executions: 30 days
    - Failed executions: 90 days (keep longer for debugging)
    - Pending/running: Never delete (might still be processing)

    Returns:
        dict: Cleanup statistics
    """
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    success_cutoff = now - timedelta(days=30)
    failed_cutoff = now - timedelta(days=90)

    # Delete old successful executions
    success_deleted, _ = Execution.objects.filter(
        status="success", created_at__lt=success_cutoff
    ).delete()

    # Delete old failed executions
    failed_deleted, _ = Execution.objects.filter(
        status="failed", created_at__lt=failed_cutoff
    ).delete()

    total_deleted = success_deleted + failed_deleted

    logger.info(
        f"[CLEANUP] Deleted {total_deleted} old executions: "
        f"{success_deleted} successful (>30 days), "
        f"{failed_deleted} failed (>90 days)"
    )

    return {
        "status": "success",
        "deleted": {
            "successful": success_deleted,
            "failed": failed_deleted,
            "total": total_deleted,
        },
        "cutoff_dates": {
            "successful": success_cutoff.isoformat(),
            "failed": failed_cutoff.isoformat(),
        },
    }


def _execute_reaction_logic(
    reaction_name: str, reaction_config: dict, trigger_data: dict, area: Area
) -> dict:
    """
    Execute the actual reaction logic.

    This is a placeholder that will be expanded in future phases.
    For now, it logs the reaction and returns success.

    Args:
        reaction_name: Name of the reaction
        reaction_config: Configuration for the reaction
        trigger_data: Data from the trigger
        area: The Area being executed

    Returns:
        dict: Result data from the reaction

    Raises:
        Exception: If reaction execution fails
    """
    logger.info(f"Executing reaction: {reaction_name}")
    logger.debug(f"Reaction config: {reaction_config}")
    logger.debug(f"Trigger data: {trigger_data}")

    # Placeholder for actual reaction implementations
    # TODO: Implement actual reactions (Phase 5)

    if reaction_name == "log_message":
        # Simple log reaction
        message = reaction_config.get("message", "AREA triggered")
        logger.info(f"[REACTION LOG] {message}")
        return {"logged": True, "message": message}

    elif reaction_name == "send_email":
        # Placeholder for email sending
        recipient = reaction_config.get("recipient")
        subject = reaction_config.get("subject", "AREA Notification")
        logger.info(f"[REACTION EMAIL] Would send to {recipient}: {subject}")
        return {
            "sent": True,
            "recipient": recipient,
            "subject": subject,
            "note": "Email sending not yet implemented",
        }

    elif reaction_name == "slack_message":
        # Placeholder for Slack message
        channel = reaction_config.get("channel")
        text = reaction_config.get("text", "AREA triggered")
        logger.info(f"[REACTION SLACK] Would send to {channel}: {text}")
        return {
            "sent": True,
            "channel": channel,
            "note": "Slack integration not yet implemented",
        }

    elif reaction_name == "teams_message":
        # Placeholder for Teams message
        webhook_url = reaction_config.get("webhook_url")
        text = reaction_config.get("text", "AREA triggered")
        logger.info(f"[REACTION TEAMS] Would send to {webhook_url}: {text}")
        return {
            "sent": True,
            "webhook_url": webhook_url,
            "note": "Teams integration not yet implemented",
        }

    else:
        # Unknown reaction - log and continue
        logger.warning(
            f"Unknown reaction type: {reaction_name}. "
            f"Marking as successful but not implemented."
        )
        return {
            "executed": False,
            "reaction": reaction_name,
            "note": f"Reaction '{reaction_name}' not yet implemented",
        }


# ==================== Admin/Debug Tasks ====================


@shared_task(name="automations.test_execution_flow")
def test_execution_flow(area_id: int):
    """
    Test task to manually trigger an execution for an area.

    Useful for testing and debugging.

    Args:
        area_id: ID of the Area to test

    Returns:
        dict: Result of the test execution
    """
    logger.info(f"Test execution flow for area #{area_id}")

    try:
        area = Area.objects.select_related("action", "reaction").get(pk=area_id)

        # Create test execution
        event_id = f"test_{area_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"

        execution, created = create_execution_safe(
            area=area,
            external_event_id=event_id,
            trigger_data={
                "test": True,
                "timestamp": timezone.now().isoformat(),
                "note": "Manual test execution",
            },
        )

        if created and execution:
            # Execute reaction asynchronously
            result = execute_reaction_task.delay(execution.pk)

            return {
                "status": "success",
                "area_id": area_id,
                "execution_id": execution.pk,
                "task_id": result.id,
            }
        else:
            return {
                "status": "duplicate",
                "area_id": area_id,
                "note": "Execution already exists (idempotency)",
            }

    except Area.DoesNotExist:
        logger.error(f"Area #{area_id} not found")
        return {"status": "error", "message": f"Area #{area_id} not found"}

    except Exception as e:
        logger.error(f"Error in test_execution_flow: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
