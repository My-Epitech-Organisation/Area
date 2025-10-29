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

import requests
from celery import shared_task

from django.db import IntegrityError, OperationalError
from django.utils import timezone

from .models import ActionState, Area, Execution

logger = logging.getLogger(__name__)


# ==================== Recoverable Exceptions ====================
# These are transient errors that are safe to retry

RECOVERABLE_EXCEPTIONS = (
    # Network and HTTP errors
    requests.exceptions.RequestException,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.HTTPError,
    # Database temporary errors
    OperationalError,  # Database connection issues
    IntegrityError,  # Concurrent inserts (idempotency)
    # Add more as needed
)


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
        Area.objects.filter(action__name__in=action_names, status=Area.Status.ACTIVE)
        .select_related(
            "action",
            "reaction",
            "action__service",
            "reaction__service",
            "owner",
        )
        .all()
    )


def validate_timer_config(
    action_name: str, action_config: dict
) -> tuple[bool, Optional[str]]:
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
            return (
                False,
                f"day_of_week must be an integer between 0 and 6, got {day_of_week}",
            )

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

        return current_time.hour == target_hour and current_time.minute == target_minute

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
        execute_reaction_task.delay(execution.pk)
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
        raise self.retry(exc=exc, countdown=60) from None


@shared_task(
    name="automations.check_github_actions",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def check_github_actions(self):
    """
    Check GitHub-based actions with smart webhook fallback.

    This task implements intelligent per-user polling:
    - Users WITH GitHub App installed: Skip (use real-time webhooks)
    - Users WITHOUT GitHub App: Use polling as fallback (5-minute intervals)

    This approach allows mixed deployments where some users benefit from
    instant webhook notifications while others use polling until they
    install the GitHub App.

    To enable webhooks:
    1. Configure WEBHOOK_SECRETS['github'] in settings
    2. User installs GitHub App from frontend
    3. GitHub App automatically configures webhooks for user's repos

    Returns:
        dict: Statistics about processed GitHub events
    """
    from django.conf import settings
    from .models import GitHubAppInstallation

    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
    webhook_configured = bool(webhook_secrets.get("github"))

    if not webhook_configured:
        logger.warning(
            "GitHub webhook secret not configured. "
            "Polling ALL users (no webhook validation possible)."
        )

    logger.info("Starting GitHub actions check (smart polling mode)")

    triggered_count = 0
    skipped_count = 0
    no_token_count = 0
    webhook_users_count = 0

    try:
        from users.oauth.manager import OAuthManager

        # Get all active areas with GitHub actions
        github_areas = get_active_areas(["github_new_issue", "github_new_pr"])

        if not github_areas:
            logger.info("No active GitHub areas found")
            return {
                "status": "no_areas",
                "checked": 0
            }

        logger.debug(f"Found {len(github_areas)} active GitHub areas")

        # Get set of user IDs with active GitHub App installation
        users_with_app = set()
        if webhook_configured:
            users_with_app = set(
                GitHubAppInstallation.objects.filter(
                    is_active=True
                ).values_list('user_id', flat=True)
            )

            if users_with_app:
                logger.info(
                    f"Found {len(users_with_app)} users with GitHub App installed "
                    f"(will use webhooks, skip polling)"
                )

        # Filter areas: only poll for users without GitHub App
        areas_needing_polling = [
            area for area in github_areas
            if area.owner_id not in users_with_app
        ]

        webhook_users_count = len(github_areas) - len(areas_needing_polling)

        if not areas_needing_polling:
            logger.info(
                "All users have GitHub App installed. "
                "No polling needed (all using webhooks)."
            )
            return {
                "status": "skipped",
                "reason": "all_users_have_webhooks",
                "webhook_users": webhook_users_count,
                "polling_users": 0,
                "message": "All GitHub users have webhooks configured"
            }

        logger.info(
            f"Polling for {len(areas_needing_polling)} areas from "
            f"{len(set(a.owner_id for a in areas_needing_polling))} users without GitHub App. "
            f"({webhook_users_count} areas using webhooks)"
        )

        for area in areas_needing_polling:
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

                # Get repository from action_config
                repository = area.action_config.get("repository")
                if not repository:
                    logger.warning(
                        f"Area {area.id}: No repository configured in action_config"
                    )
                    skipped_count += 1
                    continue

                # Validate repository format ("owner/repo")
                if repository.count("/") != 1:
                    logger.warning(
                        f"Area {area.id}: Invalid repository format '{repository}'. Expected 'owner/repo'."
                    )
                    skipped_count += 1
                    continue
                owner_repo, repo_name = repository.split("/")

                # Get or create ActionState for tracking
                from .models import ActionState

                action_state, created = ActionState.objects.get_or_create(area=area)

                # Prepare API request
                api_url = (
                    f"https://api.github.com/repos/{owner_repo}/{repo_name}/issues"
                )
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }

                # Use 'since' parameter if we have a last_checked_at
                params = {
                    "state": "all",  # Get both open and closed
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 30,
                }

                if action_state.last_checked_at:
                    # Only get issues created since last check
                    params["since"] = action_state.last_checked_at.isoformat()

                logger.debug(
                    f"Polling GitHub API for area {area.id}: "
                    f"{api_url} (since={action_state.last_checked_at})"
                )

                # Call GitHub API
                response = requests.get(
                    api_url, headers=headers, params=params, timeout=10
                )

                if response.status_code == 200:
                    issues = response.json()

                    # Filter: only process new issues (not pull requests)
                    new_issues = [
                        issue
                        for issue in issues
                        if "pull_request" not in issue  # PRs are returned as issues
                    ]

                    # Apply label filter if specified
                    label_filter = area.action_config.get("labels", [])
                    if label_filter:
                        new_issues = [
                            issue
                            for issue in new_issues
                            if any(
                                label["name"] in label_filter
                                for label in issue.get("labels", [])
                            )
                        ]

                    logger.info(
                        f"Area {area.id}: Found {len(new_issues)} new issues in {repository}"
                    )

                    # Create executions for each new issue
                    for issue in new_issues:
                        issue_id = issue["id"]
                        issue_number = issue["number"]
                        issue_title = issue["title"]
                        issue_url = issue["html_url"]

                        # Create unique event ID
                        event_id = f"github_issue_{repository}_{issue_id}"

                        # Prepare trigger data
                        trigger_data = {
                            "issue_id": issue_id,
                            "issue_number": issue_number,
                            "issue_title": issue_title,
                            "issue_url": issue_url,
                            "repository": repository,
                            "author": issue["user"]["login"],
                            "created_at": issue["created_at"],
                            "labels": [
                                label["name"] for label in issue.get("labels", [])
                            ],
                        }

                        # Create execution (with idempotency)
                        execution, was_created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if was_created and execution:
                            logger.info(
                                f"✅ Created execution for issue #{issue_number} "
                                f"in {repository}"
                            )

                            # Execute reaction asynchronously
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1
                        else:
                            logger.debug(
                                f"Skipped duplicate issue #{issue_number} in {repository}"
                            )

                    # Update last_checked_at to now
                    action_state.last_checked_at = timezone.now()
                    action_state.save(update_fields=["last_checked_at"])

                elif response.status_code == 304:
                    # Not modified (when using ETag)
                    logger.debug(f"Area {area.id}: No changes in {repository}")
                    skipped_count += 1

                elif response.status_code in [401, 403]:
                    logger.error(
                        f"Area {area.id}: GitHub auth error {response.status_code} "
                        f"for {repository}"
                    )
                    no_token_count += 1

                elif response.status_code == 404:
                    logger.error(
                        f"Area {area.id}: Repository {repository} not found or no access"
                    )
                    skipped_count += 1

                else:
                    logger.error(
                        f"Area {area.id}: GitHub API error {response.status_code}: "
                        f"{response.text}"
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
            f"Triggered: {triggered_count}, Skipped: {skipped_count}, "
            f"No token: {no_token_count}, Webhook users: {webhook_users_count}"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "no_token": no_token_count,
            "webhook_users": webhook_users_count,
            "polling_users": len(set(a.owner_id for a in areas_needing_polling)),
            "checked_areas": len(areas_needing_polling),
            "note": "Smart polling: users with GitHub App use webhooks, others use polling",
        }

    except Exception as exc:
        logger.error(f"Error in check_github_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300) from None


@shared_task(
    name="automations.check_gmail_actions",
    bind=True,
    max_retries=3,
    autoretry_for=RECOVERABLE_EXCEPTIONS,
)
def check_gmail_actions(self):
    """
    Poll Gmail for new messages matching user's action criteria.

    Checks all active Areas with Gmail actions and triggers executions
    when new matching emails are found.

    Supported actions:
    - gmail_new_email: Any new unread email
    - gmail_new_from_sender: Email from specific sender
    - gmail_new_with_label: Email with specific label
    - gmail_new_with_subject: Email with subject containing text

    Returns:
        dict: Summary of polling results
    """
    from users.oauth.manager import OAuthManager

    from .helpers.gmail_helper import get_message_details, list_messages

    logger.info("Checking Gmail actions...")

    try:
        # Get all active Areas with Gmail actions
        gmail_areas = get_active_areas(service_name="gmail")

        if not gmail_areas:
            logger.info("No active Gmail areas found")
            return {"status": "no_areas", "checked": 0}

        triggered_count = 0
        skipped_count = 0
        no_token_count = 0

        for area in gmail_areas:
            try:
                # Get valid Gmail token (via Google OAuth)
                access_token = OAuthManager.get_valid_token(area.owner, "google")

                if not access_token:
                    logger.warning(
                        f"No valid Google token for user {area.owner.username}, "
                        f"area '{area.name}'"
                    )
                    no_token_count += 1
                    continue

                # Build Gmail query based on action config
                query = _build_gmail_query(area)

                # Get last checked state
                state, _ = ActionState.objects.get_or_create(area=area)

                # List messages (newest first)
                messages = list_messages(access_token, query=query, max_results=5)

                if not messages:
                    logger.debug(f"No messages found for area '{area.name}'")
                    state.last_checked_at = timezone.now()
                    state.save()
                    continue

                # Process messages (newest first)
                new_messages_found = False

                for msg in messages:
                    msg_id = msg["id"]

                    # Check if already processed
                    if state.last_event_id == msg_id:
                        logger.debug(
                            f"Message {msg_id} already processed for area '{area.name}'"
                        )
                        break  # Since Gmail returns newest first, we can stop

                    # Get message details
                    details = get_message_details(access_token, msg_id)

                    # Create execution
                    event_id = f"gmail_{msg_id}"
                    trigger_data = {
                        "service": "gmail",
                        "action": area.action.name,
                        "message_id": msg_id,
                        "subject": details["subject"],
                        "from": details["from"],
                        "to": details["to"],
                        "date": details["date"],
                        "snippet": details["snippet"],
                        "labels": details["labels"],
                    }

                    execution, created = create_execution_safe(
                        area=area, external_event_id=event_id, trigger_data=trigger_data
                    )

                    if created and execution:
                        logger.info(
                            f"Gmail action triggered for area '{area.name}': "
                            f"Message from {details['from']}, subject: {details['subject']}"
                        )
                        execute_reaction_task.delay(execution.pk)
                        triggered_count += 1
                        new_messages_found = True

                        # Update state with newest message (only once)
                        if not state.last_event_id:
                            state.last_event_id = msg_id

                # Update state with newest message ID
                if new_messages_found or not state.last_event_id:
                    state.last_event_id = messages[0]["id"]

                state.last_checked_at = timezone.now()
                state.save()

            except Exception as e:
                logger.error(
                    f"Error checking Gmail for area '{area.name}': {e}", exc_info=True
                )
                skipped_count += 1
                continue

        logger.info(
            f"Gmail check complete: {triggered_count} triggered, "
            f"{skipped_count} skipped, {no_token_count} no token"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "no_token": no_token_count,
            "checked_areas": len(gmail_areas),
        }

    except Exception as exc:
        logger.error(f"Error in check_gmail_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300) from None


@shared_task(
    name="automations.check_weather_actions",
    bind=True,
    max_retries=3,
    autoretry_for=RECOVERABLE_EXCEPTIONS,
)
def check_weather_actions(self):
    """
    Check weather-based actions and trigger executions when conditions are met.
    """
    logger.info("Starting weather actions check")

    try:
        # Get all active weather areas with specific action names
        weather_action_names = [
            "weather_rain_detected",
            "weather_snow_detected",
            "weather_temperature_above",
            "weather_temperature_below",
            "weather_extreme_heat",
            "weather_extreme_cold",
            "weather_windy",
        ]

        weather_areas = get_active_areas(weather_action_names)

        if not weather_areas:
            logger.info("No active weather areas found")
            return {"status": "no_areas", "checked": 0}

        from django.conf import settings

        api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
        if not api_key:
            logger.error("OPENWEATHER_API_KEY not configured")
            return {"status": "error", "message": "API key not configured"}

        from .helpers.weather_helper import check_weather_condition, get_weather_data

        # --- Step 1: Group areas by location to minimize API calls
        location_map = {}
        for area in weather_areas:
            location = area.action_config.get("location")
            if not location:
                logger.warning(f"Area '{area.name}' (#{area.id}) missing location")
                continue
            location_map.setdefault(location, []).append(area)

        logger.info(
            f"Grouped {len(weather_areas)} areas into {len(location_map)} locations"
        )

        api_call_count = 0
        triggered_count = 0
        skipped_count = 0
        error_count = 0

        # --- Step 2: Fetch weather data per location
        for location, grouped_areas in location_map.items():
            try:
                weather_data = get_weather_data(api_key, location)
                api_call_count += 1
            except Exception as e:
                logger.error(f"Failed to fetch weather for {location}: {e}")
                error_count += len(grouped_areas)
                continue

            # --- Step 3: Check each area with the same data
            for area in grouped_areas:
                try:
                    action_config = area.action_config
                    action_name = area.action.name

                    # Determine if condition is met based on action type
                    condition_met = False
                    threshold = action_config.get("threshold")

                    if action_name == "weather_rain_detected":
                        condition_met = check_weather_condition(
                            api_key=api_key,
                            location=location,
                            condition="rain",
                            weather_data=weather_data,
                        )

                    elif action_name == "weather_snow_detected":
                        condition_met = check_weather_condition(
                            api_key=api_key,
                            location=location,
                            condition="snow",
                            weather_data=weather_data,
                        )

                    elif action_name == "weather_temperature_above":
                        if threshold is None:
                            logger.warning(
                                f"Area '{area.name}' missing threshold for {action_name}"
                            )
                            skipped_count += 1
                            continue
                        temp = weather_data.get("temperature", 0)
                        condition_met = temp > threshold

                    elif action_name == "weather_temperature_below":
                        if threshold is None:
                            logger.warning(
                                f"Area '{area.name}' missing threshold for {action_name}"
                            )
                            skipped_count += 1
                            continue
                        temp = weather_data.get("temperature", 0)
                        condition_met = temp < threshold

                    elif action_name == "weather_extreme_heat":
                        condition_met = check_weather_condition(
                            api_key=api_key,
                            location=location,
                            condition="extreme heat",
                            threshold=35,  # Fixed threshold for extreme heat
                            weather_data=weather_data,
                        )

                    elif action_name == "weather_extreme_cold":
                        condition_met = check_weather_condition(
                            api_key=api_key,
                            location=location,
                            condition="extreme cold",
                            threshold=-10,  # Fixed threshold for extreme cold
                            weather_data=weather_data,
                        )

                    elif action_name == "weather_windy":
                        # Get threshold from config (default 50 km/h) and convert to m/s
                        threshold_kmh = action_config.get("threshold", 50)
                        threshold_ms = threshold_kmh * 0.2778  # Convert km/h to m/s

                        condition_met = check_weather_condition(
                            api_key=api_key,
                            location=location,
                            condition="windy",
                            threshold=threshold_ms,
                            weather_data=weather_data,
                        )

                    else:
                        logger.warning(
                            f"Unknown weather action: {action_name} for area '{area.name}'"
                        )
                        skipped_count += 1
                        continue

                    if condition_met:
                        now = timezone.now()
                        event_id = f"weather_{area.id}_{location}_{action_name}_{now.strftime('%Y%m%d%H')}"
                        trigger_data = {
                            "timestamp": now.isoformat(),
                            "action_type": action_name,
                            "location": location,
                            "weather_data": weather_data,
                        }

                        # Add threshold to trigger data if applicable
                        if threshold is not None:
                            trigger_data["threshold"] = threshold

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"✅ Weather condition met for area '{area.name}' ({action_name}) in {location}"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1
                        else:
                            logger.debug(
                                f"Duplicate trigger skipped for area {area.name}"
                            )

                    else:
                        logger.debug(
                            f"Condition not met for area '{area.name}' ({action_name}) in {location}"
                        )

                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"Error processing area '{area.name}': {e}", exc_info=True
                    )

        logger.info(
            f"Weather check complete: {triggered_count} triggered, "
            f"{skipped_count} skipped, {error_count} errors "
            f"(total: {len(weather_areas)} areas)"
        )

        logger.info(f"🌦 Total weather API calls this cycle: {api_call_count}")

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "errors": error_count,
            "checked_areas": len(weather_areas),
            "locations": len(location_map),
            "api_calls": api_call_count,
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Fatal error in check_weather_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300) from None


def _build_gmail_query(area: Area) -> str:
    """
    Build Gmail API query from action configuration.

    Args:
        area: Area instance with action config

    Returns:
        str: Gmail search query string
    """
    action_name = area.action.name
    config = area.action_config

    if action_name == "gmail_new_email":
        # Any new unread email
        return "is:unread"

    elif action_name == "gmail_new_from_sender":
        # Email from specific sender
        sender = config.get("sender", "")
        if sender:
            return f"from:{sender} is:unread"
        return "is:unread"

    elif action_name == "gmail_new_with_label":
        # Email with specific label
        label = config.get("label", "")
        if label:
            return f"label:{label} is:unread"
        return "is:unread"

    elif action_name == "gmail_new_with_subject":
        # Email with subject containing text
        subject = config.get("subject_contains", "")
        if subject:
            return f"subject:{subject} is:unread"
        return "is:unread"

    else:
        # Default: any unread email
        logger.warning(f"Unknown Gmail action: {action_name}, using default query")
        return "is:unread"


@shared_task(
    name="automations.check_twitch_actions",
    bind=True,
    max_retries=3,
    autoretry_for=RECOVERABLE_EXCEPTIONS,
)
def check_twitch_actions(self):
    """
    Poll Twitch for stream status changes and other events (DEPRECATED - USE WEBHOOKS).

    ⚠️ WARNING: This polling task is DEPRECATED. Twitch EventSub webhooks provide:
    - Real-time notifications (< 1 second vs 5 minutes)
    - Better reliability (no missed events)
    - Lower API usage (no polling overhead)

    To enable webhooks:
    1. Configure WEBHOOK_SECRETS['twitch'] in settings
    2. Create EventSub subscriptions via Twitch API or management command
    3. Point webhook to: https://your-domain.com/webhooks/twitch/
    4. Subscribe to: stream.online, stream.offline, channel.follow, channel.subscribe

    Supported actions (when polling is enabled):
    - twitch_stream_online: Stream goes live
    - twitch_stream_offline: Stream goes offline
    - twitch_new_follower: New follower
    - twitch_new_subscriber: New subscription
    - twitch_channel_update: Channel info changes

    Returns:
        dict: Summary of polling results
    """
    logger.warning(
        "Twitch polling is DEPRECATED. Use EventSub webhooks for production. "
        "See: https://dev.twitch.tv/docs/eventsub"
    )

    # Return early if webhooks are configured
    from django.conf import settings
    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
    if webhook_secrets.get("twitch"):
        logger.info(
            "Twitch webhook is configured. Skipping polling task. "
            "Remove this task from Celery Beat schedule."
        )
        return {
            "status": "skipped",
            "reason": "webhooks_enabled",
            "message": "Twitch EventSub webhooks are configured. Polling is disabled.",
        }

    from django.conf import settings

    from users.oauth.manager import OAuthManager

    from .helpers.twitch_helper import (
        get_channel_info,
        get_follower_count,
        get_stream_info,
        get_user_info,
    )

    logger.info("Checking Twitch actions (polling mode - DEPRECATED)...")

    try:
        # Get all active Areas with Twitch actions
        twitch_areas = get_active_areas(
            [
                "twitch_stream_online",
                "twitch_stream_offline",
                "twitch_new_follower",
                "twitch_channel_update",
            ]
        )

        if not twitch_areas:
            logger.info("No active Twitch areas found")
            return {"status": "no_areas", "checked": 0}

        triggered_count = 0
        skipped_count = 0
        no_token_count = 0

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        for area in twitch_areas:
            try:
                # Get valid Twitch token
                access_token = OAuthManager.get_valid_token(area.owner, "twitch")

                if not access_token:
                    logger.warning(
                        f"No valid Twitch token for user {area.owner.username}, "
                        f"area '{area.name}'"
                    )
                    no_token_count += 1
                    continue

                action_name = area.action.name

                # Get or create ActionState for tracking
                from .models import ActionState

                state, _ = ActionState.objects.get_or_create(area=area)

                # Handle stream online/offline actions
                if action_name in ["twitch_stream_online", "twitch_stream_offline"]:
                    # Get broadcaster from config or use authenticated user
                    broadcaster_login = area.action_config.get("broadcaster_login")

                    if broadcaster_login:
                        user_info = get_user_info(
                            access_token, client_id, user_login=broadcaster_login
                        )
                    else:
                        user_info = get_user_info(access_token, client_id)

                    broadcaster_id = user_info["id"]
                    broadcaster_login = user_info["login"]

                    # Check if stream is live
                    stream_info = get_stream_info(
                        access_token, client_id, broadcaster_id
                    )
                    is_live = stream_info is not None

                    # Get previous state
                    previous_state = state.metadata.get("is_live", False)

                    # Detect state change
                    if (
                        action_name == "twitch_stream_online"
                        and is_live
                        and not previous_state
                    ):
                        # Stream just went online
                        event_id = f"twitch_online_{broadcaster_id}_{stream_info['started_at']}"

                        trigger_data = {
                            "service": "twitch",
                            "action": action_name,
                            "broadcaster_id": broadcaster_id,
                            "broadcaster_login": broadcaster_login,
                            "stream_id": stream_info["id"],
                            "title": stream_info["title"],
                            "game_name": stream_info["game_name"],
                            "viewer_count": stream_info["viewer_count"],
                            "started_at": stream_info["started_at"],
                        }

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Twitch stream online triggered for '{area.name}': "
                                f"{broadcaster_login} - {stream_info['title']}"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1

                        # Update state
                        state.metadata["is_live"] = True
                        state.last_checked_at = timezone.now()
                        state.save()

                    elif (
                        action_name == "twitch_stream_offline"
                        and not is_live
                        and previous_state
                    ):
                        # Stream just went offline
                        event_id = f"twitch_offline_{broadcaster_id}_{timezone.now().isoformat()}"

                        trigger_data = {
                            "service": "twitch",
                            "action": action_name,
                            "broadcaster_id": broadcaster_id,
                            "broadcaster_login": broadcaster_login,
                            "offline_at": timezone.now().isoformat(),
                        }

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Twitch stream offline triggered for '{area.name}': "
                                f"{broadcaster_login}"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1

                        # Update state
                        state.metadata["is_live"] = False
                        state.last_checked_at = timezone.now()
                        state.save()

                    else:
                        # No state change
                        state.metadata["is_live"] = is_live
                        state.last_checked_at = timezone.now()
                        state.save()

                # Handle follower count changes
                elif action_name == "twitch_new_follower":
                    user_info = get_user_info(access_token, client_id)
                    broadcaster_id = user_info["id"]

                    # Get current follower count
                    current_count = get_follower_count(
                        access_token, client_id, broadcaster_id
                    )

                    # Get previous count
                    previous_count = state.metadata.get("follower_count", current_count)

                    if current_count > previous_count:
                        # New followers detected
                        new_followers = current_count - previous_count

                        event_id = f"twitch_follower_{broadcaster_id}_{timezone.now().isoformat()}"

                        trigger_data = {
                            "service": "twitch",
                            "action": action_name,
                            "broadcaster_id": broadcaster_id,
                            "broadcaster_login": user_info["login"],
                            "new_follower_count": new_followers,
                            "total_followers": current_count,
                            "detected_at": timezone.now().isoformat(),
                        }

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Twitch new follower triggered for '{area.name}': "
                                f"+{new_followers} followers (total: {current_count})"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1

                    # Update state
                    state.metadata["follower_count"] = current_count
                    state.last_checked_at = timezone.now()
                    state.save()

                # Handle channel info changes
                elif action_name == "twitch_channel_update":
                    user_info = get_user_info(access_token, client_id)
                    broadcaster_id = user_info["id"]

                    # Get current channel info
                    channel_info = get_channel_info(
                        access_token, client_id, broadcaster_id
                    )

                    # Get previous info
                    previous_title = state.metadata.get("channel_title", "")
                    previous_game = state.metadata.get("channel_game", "")

                    current_title = channel_info["title"]
                    current_game = channel_info["game_name"]

                    # Detect changes
                    if current_title != previous_title or current_game != previous_game:
                        event_id = f"twitch_update_{broadcaster_id}_{timezone.now().isoformat()}"

                        trigger_data = {
                            "service": "twitch",
                            "action": action_name,
                            "broadcaster_id": broadcaster_id,
                            "broadcaster_login": user_info["login"],
                            "new_title": current_title,
                            "old_title": previous_title,
                            "new_game": current_game,
                            "old_game": previous_game,
                            "changed_at": timezone.now().isoformat(),
                        }

                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Twitch channel update triggered for '{area.name}': "
                                f"{current_title} - {current_game}"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1

                    # Update state
                    state.metadata["channel_title"] = current_title
                    state.metadata["channel_game"] = current_game
                    state.last_checked_at = timezone.now()
                    state.save()

            except Exception as e:
                logger.error(
                    f"Error checking Twitch for area '{area.name}': {e}", exc_info=True
                )
                skipped_count += 1
                continue

        logger.info(
            f"Twitch check complete: {triggered_count} triggered, "
            f"{skipped_count} skipped, {no_token_count} no token"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "no_token": no_token_count,
            "checked_areas": len(twitch_areas),
            "note": "For production, use EventSub webhooks for real-time events",
        }

    except Exception as exc:
        logger.error(f"Error in check_twitch_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300) from None


@shared_task(
    name="automations.check_slack_actions",
    bind=True,
    max_retries=3,
    autoretry_for=RECOVERABLE_EXCEPTIONS,
)
def check_slack_actions(self):
    """
    Poll Slack for new messages and events (DEPRECATED - USE WEBHOOKS).

    ⚠️ WARNING: This polling task is DEPRECATED. Slack Events API provides:
    - Real-time event delivery
    - Better message ordering and reliability
    - Reduced API rate limit usage

    To enable webhooks:
    1. Configure WEBHOOK_SECRETS['slack'] in settings
    2. Enable Events API in your Slack App settings
    3. Subscribe to events: message.channels, app_mention, member_joined_channel
    4. Point Request URL to: https://your-domain.com/webhooks/slack/

    Supported actions (when polling is enabled):
    - slack_new_message: Any new message in a channel
    - slack_message_with_keyword: Message containing specific keyword
    - slack_user_mention: User mentioned in a message
    - slack_channel_join: User joins a channel

    Returns:
        dict: Summary of polling results
    """
    logger.warning(
        "Slack polling is DEPRECATED. Use Slack Events API for production. "
        "See: https://api.slack.com/events-api"
    )

    # Return early if webhooks are configured
    from django.conf import settings
    webhook_secrets = getattr(settings, "WEBHOOK_SECRETS", {})
    if webhook_secrets.get("slack"):
        logger.info(
            "Slack webhook is configured. Skipping polling task. "
            "Remove this task from Celery Beat schedule."
        )
        return {
            "status": "skipped",
            "reason": "webhooks_enabled",
            "message": "Slack Events API webhooks are configured. Polling is disabled.",
        }

    from users.oauth.manager import OAuthManager

    from .helpers.slack_helper import (
        get_channel_history,
        parse_message_event,
    )

    logger.info("Checking Slack actions (polling mode - DEPRECATED)...")

    try:
        # Get all active Areas with Slack actions
        slack_areas = get_active_areas(
            [
                "slack_new_message",
                "slack_message_with_keyword",
                "slack_user_mention",
                "slack_channel_join",
            ]
        )

        if not slack_areas:
            logger.info("No active Slack areas found")
            return {"status": "no_areas", "checked": 0}

        triggered_count = 0
        skipped_count = 0
        no_token_count = 0

        for area in slack_areas:
            try:
                # Get valid Slack token
                access_token = OAuthManager.get_valid_token(area.owner, "slack")

                if not access_token:
                    logger.warning(
                        f"No valid Slack token for user {area.owner.username}, "
                        f"area '{area.name}'"
                    )
                    no_token_count += 1
                    continue

                # Get the authenticated user's Slack ID for mention detection
                try:
                    from users.oauth.slack import SlackOAuthProvider

                    provider = SlackOAuthProvider(
                        None
                    )  # Config not needed for get_user_info
                    user_info = provider.get_user_info(access_token)
                    authenticated_user_id = user_info["id"]
                    logger.debug(
                        f"Authenticated Slack user ID for {area.owner.username}: {authenticated_user_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to get Slack user info for {area.owner.username}: {e}"
                    )
                    skipped_count += 1
                    continue

                action_name = area.action.name
                action_config = area.action_config

                # Get or create ActionState for tracking
                from .models import ActionState

                state, _ = ActionState.objects.get_or_create(area=area)

                # Get channel from config
                channel = action_config.get("channel")
                if not channel:
                    logger.warning(f"Area '{area.name}' missing channel configuration")
                    skipped_count += 1
                    continue

                # Get channel history (newest messages first)
                # Use 'since' parameter if we have a last_checked_at
                params = {"limit": 50}  # Get up to 50 recent messages
                if state.last_checked_at:
                    # Convert to Unix timestamp for Slack API
                    since_ts = state.last_checked_at.timestamp()
                    params["oldest"] = str(since_ts)

                logger.debug(f"Polling Slack channel {channel} for area '{area.name}'")

                try:
                    messages = get_channel_history(access_token, channel, **params)
                except Exception as e:
                    logger.error(f"Failed to get channel history for {channel}: {e}")
                    skipped_count += 1
                    continue

                if not messages:
                    logger.debug(f"No messages found in channel {channel}")
                    state.last_checked_at = timezone.now()
                    state.save()
                    continue

                # Process messages (they come newest first)
                new_events_found = False

                for message in messages:
                    message_ts = message.get("ts")
                    if not message_ts:
                        continue

                    # Parse the message event
                    event_data = parse_message_event(message)

                    # Skip bot messages and system messages (but allow channel_join events)
                    subtype = event_data.get("subtype")
                    if event_data.get("bot_id") or (
                        subtype and subtype != "channel_join"
                    ):
                        continue

                    # Create unique event ID
                    event_id = f"slack_{channel}_{message_ts}"

                    # Check if already processed
                    if state.last_event_id == event_id:
                        logger.debug(f"Message {event_id} already processed")
                        break  # Since messages are newest first, we can stop

                    # Check action-specific conditions
                    should_trigger = False
                    trigger_data = {
                        "service": "slack",
                        "action": action_name,
                        "channel": channel,
                        "message_ts": message_ts,
                        "user": event_data.get("user", "unknown"),
                        "text": event_data.get("text", ""),
                        "timestamp": event_data.get("timestamp"),
                    }

                    if action_name == "slack_new_message":
                        # Any new message
                        should_trigger = True

                    elif action_name == "slack_message_with_keyword":
                        # Check for keyword in message text
                        keyword = action_config.get("keywords", "").lower()
                        message_text = event_data.get("text", "").lower()
                        if keyword and keyword in message_text:
                            should_trigger = True
                            trigger_data["keywords"] = keyword

                    elif action_name == "slack_user_mention":
                        # Check if the authenticated user is mentioned
                        if f"<@{authenticated_user_id}>" in event_data.get("text", ""):
                            should_trigger = True
                            trigger_data["mentioned_user"] = authenticated_user_id

                    elif (
                        action_name == "slack_channel_join"
                        and event_data.get("subtype") == "channel_join"
                    ):
                        should_trigger = True

                    if should_trigger:
                        # Create execution (with idempotency)
                        execution, created = create_execution_safe(
                            area=area,
                            external_event_id=event_id,
                            trigger_data=trigger_data,
                        )

                        if created and execution:
                            logger.info(
                                f"Slack action triggered for '{area.name}': "
                                f"{action_name} in {channel}"
                            )
                            execute_reaction_task.delay(execution.pk)
                            triggered_count += 1
                            new_events_found = True

                # Update state
                if (new_events_found or not state.last_event_id) and messages:
                    latest_ts = messages[0].get("ts")
                    if latest_ts:
                        state.last_event_id = f"slack_{channel}_{latest_ts}"

                state.last_checked_at = timezone.now()
                state.save()

            except Exception as e:
                logger.error(
                    f"Error checking Slack for area '{area.name}': {e}", exc_info=True
                )
                skipped_count += 1
                continue

        logger.info(
            f"Slack check complete: {triggered_count} triggered, "
            f"{skipped_count} skipped, {no_token_count} no token"
        )

        return {
            "status": "success",
            "triggered": triggered_count,
            "skipped": skipped_count,
            "no_token": no_token_count,
            "checked_areas": len(slack_areas),
            "note": "Slack Events API webhooks preferred over polling",
        }

    except Exception as exc:
        logger.error(f"Error in check_slack_actions: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300) from None


@shared_task(
    name="automations.execute_reaction_task",
    bind=True,
    max_retries=3,
    autoretry_for=RECOVERABLE_EXCEPTIONS,  # Only retry transient errors
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
            f"area '{execution.area.name}' "
            f"(attempt {retry_count + 1}/{self.max_retries + 1})"
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
                f"Max retries ({self.max_retries}) exceeded for "
                f"execution #{execution_id}. Moving to dead letter queue."
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
    from django.db.models import Count, Q
    from django.utils import timezone

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

    # ==================== Slack Reactions ====================
    elif reaction_name == "slack_send_message":
        # Real implementation: Send message to Slack channel
        from users.oauth.manager import OAuthManager

        from .helpers.slack_helper import post_message

        channel = reaction_config.get("channel")
        message = reaction_config.get("message", "AREA triggered")

        if not channel:
            raise ValueError("Channel is required for slack_send_message")

        # Get valid Slack token
        access_token = OAuthManager.get_valid_token(area.owner, "slack")
        if not access_token:
            raise ValueError(f"No valid Slack token for user {area.owner.username}")

        try:
            result = post_message(access_token, channel, message)

            logger.info(f"[REACTION SLACK] Sent message to {channel}: {message}")
            return {
                "success": True,
                "channel": channel,
                "message_ts": result.get("ts"),
                "message": message,
            }

        except Exception as e:
            logger.error(f"[REACTION SLACK] Failed to send message: {e}")
            raise ValueError(f"Slack send_message failed: {str(e)}") from e

    elif reaction_name == "slack_send_alert":
        # Real implementation: Send alert message to Slack channel
        from django.utils import timezone

        from users.oauth.manager import OAuthManager

        from .helpers.slack_helper import post_message

        channel = reaction_config.get("channel")
        alert_type = reaction_config.get("alert_type", "info")
        title = reaction_config.get("title", "🚨 AREA Alert Triggered")
        details = reaction_config.get("details", "")

        # Map alert_type to Slack color
        color_map = {"info": "good", "warning": "warning", "error": "danger"}
        color = color_map.get(alert_type, "good")

        if not channel:
            raise ValueError("Channel is required for slack_send_alert")

        # Format as Slack attachment for better visibility
        attachment = {
            "color": color,
            "text": title,
            "footer": "AREA Automation",
            "ts": int(timezone.now().timestamp()),
        }

        # Add details if provided
        if details:
            attachment["text"] += f"\n\n{details}"

        # Get valid Slack token
        access_token = OAuthManager.get_valid_token(area.owner, "slack")
        if not access_token:
            raise ValueError(f"No valid Slack token for user {area.owner.username}")

        try:
            result = post_message(access_token, channel, "", attachments=[attachment])

            logger.info(f"[REACTION SLACK] Sent alert to {channel}: {title}")
            return {
                "success": True,
                "channel": channel,
                "message_ts": result.get("ts"),
                "alert_type": alert_type,
                "title": title,
                "details": details,
            }

        except Exception as e:
            logger.error(f"[REACTION SLACK] Failed to send alert: {e}")
            raise ValueError(f"Slack send_alert failed: {str(e)}") from e

    elif reaction_name == "slack_post_update":
        # Real implementation: Post an update/status message
        from users.oauth.manager import OAuthManager

        from .helpers.slack_helper import post_message

        channel = reaction_config.get("channel")
        title = reaction_config.get("title", "AREA Update")
        status = reaction_config.get("status", "Update")
        details = reaction_config.get("details", "")

        if not channel:
            raise ValueError("Channel is required for slack_post_update")

        # Format as a nicely structured message
        message_text = f"📢 *{title}*\n\n*{status}*"
        if details:
            message_text += f"\n\n{details}"

        # Get valid Slack token
        access_token = OAuthManager.get_valid_token(area.owner, "slack")
        if not access_token:
            raise ValueError(f"No valid Slack token for user {area.owner.username}")

        try:
            result = post_message(access_token, channel, message_text)

            logger.info(f"[REACTION SLACK] Posted update to {channel}: {title}")
            return {
                "success": True,
                "channel": channel,
                "message_ts": result.get("ts"),
                "title": title,
                "status": status,
            }

        except Exception as e:
            logger.error(f"[REACTION SLACK] Failed to post update: {e}")
            raise ValueError(f"Slack post_update failed: {str(e)}") from e

    elif reaction_name == "github_create_issue":
        # Real implementation: Create GitHub issue via API
        repository = reaction_config.get("repository")
        title = reaction_config.get("title", "Automated Issue")
        body = reaction_config.get("body", "")
        labels = reaction_config.get("labels", [])
        assignees = reaction_config.get("assignees", [])

        if not repository:
            raise ValueError("Repository is required for github_create_issue")

        # Get valid GitHub OAuth token for the user
        from users.oauth.manager import OAuthManager

        try:
            access_token = OAuthManager.get_valid_token(area.owner, "github")
            if not access_token:
                raise ValueError(
                    f"No valid GitHub token for user {area.owner.username}"
                )

            # Prepare API request
            owner, repo = repository.split("/")
            api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"

            payload = {
                "title": title,
                "body": body,
            }

            if labels:
                payload["labels"] = labels
            if assignees:
                payload["assignees"] = assignees

            # Call GitHub API
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            logger.info(f"[REACTION GITHUB] Creating issue in {repository}: {title}")

            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            # Handle responses
            if response.status_code == 201:
                issue_data = response.json()
                issue_url = issue_data.get("html_url")
                issue_number = issue_data.get("number")

                logger.info(
                    f"[REACTION GITHUB] ✅ Issue created: {issue_url} (#{issue_number})"
                )

                return {
                    "success": True,
                    "issue_url": issue_url,
                    "issue_number": issue_number,
                    "repository": repository,
                }

            elif response.status_code == 401:
                error_msg = (
                    "GitHub authentication failed. Token may be invalid or expired."
                )
                logger.error(f"[REACTION GITHUB] ❌ {error_msg}")
                raise ValueError(error_msg)

            elif response.status_code == 403:
                error_msg = "GitHub API rate limit exceeded or access forbidden."
                logger.error(f"[REACTION GITHUB] ❌ {error_msg}")
                raise ValueError(error_msg)

            elif response.status_code == 404:
                error_msg = f"Repository {repository} not found or no access."
                logger.error(f"[REACTION GITHUB] ❌ {error_msg}")
                raise ValueError(error_msg)

            else:
                error_msg = (
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                logger.error(f"[REACTION GITHUB] ❌ {error_msg}")
                raise ValueError(error_msg)

        except requests.exceptions.Timeout as e:
            raise ValueError("GitHub API request timed out") from e
        except requests.exceptions.RequestException as e:
            raise ValueError(f"GitHub API request failed: {str(e)}") from e

    elif reaction_name == "gmail_send_email":
        # Real implementation: Send email via Gmail API
        from users.oauth.manager import OAuthManager

        from .helpers.gmail_helper import send_email

        to = reaction_config.get("to")
        subject = reaction_config.get("subject", "AREA Notification")
        body = reaction_config.get("body", "")

        if not to:
            raise ValueError("Recipient email is required for gmail_send_email")

        # Get valid Google token
        access_token = OAuthManager.get_valid_token(area.owner, "google")
        if not access_token:
            raise ValueError(f"No valid Google token for user {area.owner.username}")

        try:
            result = send_email(access_token, to, subject, body)

            logger.info(f"[REACTION GMAIL] Sent email to {to}: {subject}")
            return {
                "success": True,
                "message_id": result["id"],
                "to": to,
                "subject": subject,
            }

        except Exception as e:
            logger.error(f"[REACTION GMAIL] Failed to send email: {e}")
            raise ValueError(f"Gmail send failed: {str(e)}") from e

    elif reaction_name == "gmail_mark_read":
        # Real implementation: Mark Gmail message as read
        from users.oauth.manager import OAuthManager

        from .helpers.gmail_helper import mark_message_read

        # Get message_id from config or trigger_data
        message_id = reaction_config.get("message_id") or trigger_data.get("message_id")

        if not message_id:
            raise ValueError("Message ID required to mark as read")

        # Get valid Google token
        access_token = OAuthManager.get_valid_token(area.owner, "google")
        if not access_token:
            raise ValueError("No valid Google token")

        try:
            mark_message_read(access_token, message_id)

            logger.info(f"[REACTION GMAIL] Marked message {message_id} as read")
            return {"success": True, "message_id": message_id}

        except Exception as e:
            logger.error(f"[REACTION GMAIL] Failed to mark as read: {e}")
            raise ValueError(f"Gmail mark_read failed: {str(e)}") from e

    elif reaction_name == "gmail_add_label":
        # Real implementation: Add label to Gmail message
        from users.oauth.manager import OAuthManager

        from .helpers.gmail_helper import add_label_to_message

        # Get message_id from config or trigger_data
        message_id = reaction_config.get("message_id") or trigger_data.get("message_id")
        label_name = reaction_config.get("label")

        if not message_id or not label_name:
            raise ValueError("Message ID and label required for gmail_add_label")

        # Get valid Google token
        access_token = OAuthManager.get_valid_token(area.owner, "google")
        if not access_token:
            raise ValueError("No valid Google token")

        try:
            add_label_to_message(access_token, message_id, label_name)

            logger.info(
                f"[REACTION GMAIL] Added label '{label_name}' to message {message_id}"
            )
            return {
                "success": True,
                "message_id": message_id,
                "label": label_name,
            }

        except Exception as e:
            logger.error(f"[REACTION GMAIL] Failed to add label: {e}")
            raise ValueError(f"Gmail add_label failed: {str(e)}") from e

    elif reaction_name == "calendar_create_event":
        # Real implementation: Create Google Calendar event
        from users.oauth.manager import OAuthManager

        from .helpers.calendar_helper import create_event

        summary = reaction_config.get("summary") or reaction_config.get(
            "title", "AREA Event"
        )
        start = reaction_config.get("start")
        end = reaction_config.get("end")
        description = reaction_config.get("description", "")
        location = reaction_config.get("location", "")
        attendees = reaction_config.get("attendees", [])

        if not start or not end:
            raise ValueError(
                "start and end datetime are required for calendar_create_event"
            )

        # Get valid Google token
        access_token = OAuthManager.get_valid_token(area.owner, "google")
        if not access_token:
            raise ValueError(f"No valid Google token for user {area.owner.username}")

        try:
            result = create_event(
                access_token, summary, start, end, description, location, attendees
            )

            logger.info(
                f"[REACTION CALENDAR] Created event: {summary} ({result.get('htmlLink')})"
            )
            return {
                "success": True,
                "event_id": result["id"],
                "summary": summary,
                "link": result.get("htmlLink"),
            }

        except Exception as e:
            logger.error(f"[REACTION CALENDAR] Failed to create event: {e}")
            raise ValueError(f"Calendar create_event failed: {str(e)}") from e

    elif reaction_name == "calendar_update_event":
        # Real implementation: Update Google Calendar event
        from users.oauth.manager import OAuthManager

        from .helpers.calendar_helper import update_event

        event_id = reaction_config.get("event_id")
        summary = reaction_config.get("summary")
        start = reaction_config.get("start")
        end = reaction_config.get("end")
        description = reaction_config.get("description")

        if not event_id:
            raise ValueError("event_id is required for calendar_update_event")

        # Get valid Google token
        access_token = OAuthManager.get_valid_token(area.owner, "google")
        if not access_token:
            raise ValueError("No valid Google token")

        try:
            result = update_event(
                access_token, event_id, summary, start, end, description
            )

            logger.info(f"[REACTION CALENDAR] Updated event: {result['summary']}")
            return {
                "success": True,
                "event_id": result["id"],
                "summary": result["summary"],
            }

        except Exception as e:
            logger.error(f"[REACTION CALENDAR] Failed to update event: {e}")
            raise ValueError(f"Calendar update_event failed: {str(e)}") from e

    elif reaction_name == "webhook_post":
        # Execute webhook POST request
        url = reaction_config.get("url")
        if not url:
            raise ValueError("Webhook URL is required for webhook_post reaction")

        payload = {
            "area_id": area.id,
            "area_name": area.name,
            "trigger_data": trigger_data,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"[REACTION WEBHOOK] POST to {url}")

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()

            logger.info(f"[REACTION WEBHOOK] Success: {response.status_code}")
            return {
                "sent": True,
                "url": url,
                "status_code": response.status_code,
                "response": response.text[:500],
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"[REACTION WEBHOOK] Failed: {e}")
            raise Exception(f"Webhook POST failed: {e}") from e

    # ==================== Debug Reactions ====================
    elif reaction_name == "debug_log_execution":
        # Log execution details for debugging
        from django.utils import timezone

        custom_message = reaction_config.get("message", "Debug execution triggered")
        timestamp = timezone.now()

        log_data = {
            "timestamp": timestamp.isoformat(),
            "area_id": area.id,
            "area_name": area.name,
            "message": custom_message,
            "trigger_data": trigger_data,
            "owner": area.owner.email,
        }

        logger.info(f"[REACTION DEBUG] {custom_message} at {timestamp}")
        logger.info(f"[REACTION DEBUG] Area: {area.name} (ID: {area.id})")
        logger.info(f"[REACTION DEBUG] Trigger data: {trigger_data}")

        return log_data

    # ==================== Twitch Reactions ====================
    elif reaction_name == "twitch_send_chat_message":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import get_user_info, send_chat_message

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get user info (sender and broadcaster - same person)
        user_info = get_user_info(access_token, client_id)
        user_id = user_info["id"]
        channel_name = user_info["login"]

        # Get message from config
        message = reaction_config.get("message", "")

        # Send chat message to own channel
        send_chat_message(
            access_token,
            client_id,
            user_id,  # broadcaster_id (own channel)
            user_id,  # sender_id (yourself)
            message,
        )

        logger.info(f"[REACTION TWITCH] Sent chat message to {channel_name}: {message}")
        return {"sent": True, "message": message, "channel": channel_name}

    elif reaction_name == "twitch_send_whisper":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import get_user_info, send_whisper

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get sender info
        sender_info = get_user_info(access_token, client_id)
        sender_id = sender_info["id"]

        # Get recipient username
        to_user = reaction_config.get("to_user", "").strip()
        if not to_user:
            raise Exception("Recipient username is required for whisper")

        # Get recipient user info
        recipient_info = get_user_info(access_token, client_id, user_login=to_user)
        recipient_id = recipient_info["id"]

        # Get message
        message = reaction_config.get("message", "")

        # Send whisper
        send_whisper(
            access_token,
            client_id,
            sender_id,
            recipient_id,
            message,
        )

        logger.info(f"[REACTION TWITCH] Sent whisper to {to_user}: {message}")
        return {"sent": True, "message": message, "recipient": to_user}

    elif reaction_name == "twitch_send_announcement":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import get_user_info, send_chat_announcement

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get broadcaster info
        user_info = get_user_info(access_token, client_id)
        broadcaster_id = user_info["id"]

        # Get message and color from config
        message = reaction_config.get("message", "")
        color = reaction_config.get("color", "primary")

        # Send announcement
        send_chat_announcement(
            access_token, client_id, broadcaster_id, broadcaster_id, message, color
        )

        logger.info(f"[REACTION TWITCH] Sent announcement: {message}")
        return {"sent": True, "message": message, "color": color}

    elif reaction_name == "twitch_create_clip":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import create_clip, get_user_info

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get broadcaster info
        user_info = get_user_info(access_token, client_id)
        broadcaster_id = user_info["id"]

        # Create clip
        clip_data = create_clip(access_token, client_id, broadcaster_id)

        logger.info(f"[REACTION TWITCH] Created clip: {clip_data['id']}")
        return {
            "created": True,
            "clip_id": clip_data["id"],
            "edit_url": clip_data["edit_url"],
        }

    elif reaction_name == "twitch_update_title":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import get_user_info, modify_channel_info

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get broadcaster info
        user_info = get_user_info(access_token, client_id)
        broadcaster_id = user_info["id"]

        # Get new title from config
        new_title = reaction_config.get("title", "")

        # Update title
        modify_channel_info(access_token, client_id, broadcaster_id, title=new_title)

        logger.info(f"[REACTION TWITCH] Updated title to: {new_title}")
        return {"updated": True, "new_title": new_title}

    elif reaction_name == "twitch_update_category":
        from django.conf import settings

        from users.oauth.manager import OAuthManager

        from .helpers.twitch_helper import (
            get_user_info,
            modify_channel_info,
            search_categories,
        )

        access_token = OAuthManager.get_valid_token(area.owner, "twitch")
        if not access_token:
            raise Exception("No valid Twitch token available")

        client_id = settings.OAUTH2_PROVIDERS["twitch"]["client_id"]

        # Get broadcaster info
        user_info = get_user_info(access_token, client_id)
        broadcaster_id = user_info["id"]

        # Get game name from config
        game_name = reaction_config.get("game_name", "")

        # Search for game/category
        categories = search_categories(access_token, client_id, game_name, first=1)

        if not categories:
            raise Exception(f"Game/category not found: {game_name}")

        game_id = categories[0]["id"]

        # Update category
        modify_channel_info(access_token, client_id, broadcaster_id, game_id=game_id)

        logger.info(f"[REACTION TWITCH] Updated category to: {game_name}")
        return {"updated": True, "game_name": game_name, "game_id": game_id}

    # ==================== Spotify Reactions ====================
    elif reaction_name == "spotify_play_track":
        # Play a specific track
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import play_track

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        track_input = reaction_config.get("track_uri")
        position_ms = reaction_config.get("position_ms", 0)

        if not track_input:
            raise ValueError("Track URI/URL is required for spotify_play_track")

        # Convert URL to URI if needed
        if track_input.startswith("https://open.spotify.com"):
            # Extract track ID from URL
            # URL format: https://open.spotify.com/track/{track_id} or https://open.spotify.com/intl-{locale}/track/{track_id}
            import re

            match = re.search(r"/track/([a-zA-Z0-9]+)", track_input)
            if match:
                track_id = match.group(1)
                track_uri = f"spotify:track:{track_id}"
            else:
                raise ValueError(f"Invalid Spotify URL format: {track_input}")
        else:
            # Assume it's already a URI
            track_uri = track_input

        try:
            result = play_track(access_token, track_uri, position_ms)

            logger.info(f"[REACTION SPOTIFY] Started playing track: {track_uri}")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to play track: {e}")
            raise ValueError(f"Spotify play_track failed: {str(e)}") from e

    elif reaction_name == "spotify_pause_playback":
        # Pause current playback
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import pause_playback

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        try:
            result = pause_playback(access_token)

            logger.info("[REACTION SPOTIFY] Paused playback")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to pause playback: {e}")
            raise ValueError(f"Spotify pause_playback failed: {str(e)}") from e

    elif reaction_name == "spotify_resume_playback":
        # Resume current playback
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import resume_playback

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        try:
            result = resume_playback(access_token)

            logger.info("[REACTION SPOTIFY] Resumed playback")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to resume playback: {e}")
            raise ValueError(f"Spotify resume_playback failed: {str(e)}") from e

    elif reaction_name == "spotify_skip_next":
        # Skip to next track
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import skip_to_next

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        try:
            result = skip_to_next(access_token)

            logger.info("[REACTION SPOTIFY] Skipped to next track")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to skip next: {e}")
            raise ValueError(f"Spotify skip_next failed: {str(e)}") from e

    elif reaction_name == "spotify_skip_previous":
        # Skip to previous track
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import skip_to_previous

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        try:
            result = skip_to_previous(access_token)

            logger.info("[REACTION SPOTIFY] Skipped to previous track")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to skip previous: {e}")
            raise ValueError(f"Spotify skip_previous failed: {str(e)}") from e

    elif reaction_name == "spotify_set_volume":
        # Set playback volume
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import set_volume

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        volume_percent = reaction_config.get("volume_percent", 50)

        try:
            result = set_volume(access_token, volume_percent)

            logger.info(f"[REACTION SPOTIFY] Set volume to {volume_percent}%")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to set volume: {e}")
            raise ValueError(f"Spotify set_volume failed: {str(e)}") from e

    elif reaction_name == "spotify_create_playlist":
        # Create a new playlist
        from users.oauth.manager import OAuthManager

        from .helpers.spotify_helper import create_playlist

        access_token = OAuthManager.get_valid_token(area.owner, "spotify")
        if not access_token:
            raise ValueError(f"No valid Spotify token for user {area.owner.username}")

        name = reaction_config.get("name")
        description = reaction_config.get("description", "")
        public = reaction_config.get("public", False)

        if not name:
            raise ValueError("Playlist name is required for spotify_create_playlist")

        try:
            result = create_playlist(access_token, name, description, public)

            logger.info(f"[REACTION SPOTIFY] Created playlist: {name}")
            return result

        except Exception as e:
            logger.error(f"[REACTION SPOTIFY] Failed to create playlist: {e}")
            raise ValueError(f"Spotify create_playlist failed: {str(e)}") from e

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
