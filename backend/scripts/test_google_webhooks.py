#!/usr/bin/env python3
"""
Test Google Webhooks Setup

This script verifies the Google webhook infrastructure is correctly configured.
Run with: python scripts/test_google_webhooks.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "area_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from automations.models import GoogleWebhookWatch, Area
from automations.tasks import (
    setup_google_watches_for_user,
    renew_google_watches,
    setup_youtube_watches,
)

User = get_user_model()


def test_model():
    """Test GoogleWebhookWatch model"""
    print("\n🧪 Testing GoogleWebhookWatch Model...")

    # Check model is registered
    try:
        watch_count = GoogleWebhookWatch.objects.count()
        print(f"✅ Model accessible - {watch_count} watches in database")
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

    # Test creating a watch
    try:
        user = User.objects.first()
        if not user:
            print("⚠️  No users found, skipping watch creation test")
            return True

        watch, created = GoogleWebhookWatch.objects.get_or_create(
            user=user,
            service=GoogleWebhookWatch.Service.GMAIL,
            channel_id="test-channel-123",
            defaults={
                "resource_id": "test-resource",
                "resource_uri": "primary",
                "expiration": timezone.now() + timezone.timedelta(days=7),
            },
        )

        if created:
            print(f"✅ Test watch created: {watch}")
            watch.delete()  # Cleanup
        else:
            print(f"✅ Watch already exists: {watch}")

        return True

    except Exception as e:
        print(f"❌ Watch creation failed: {e}")
        return False


def test_tasks():
    """Test Celery tasks are registered"""
    print("\n🧪 Testing Celery Tasks...")

    tasks = [
        ("setup_google_watches_for_user", setup_google_watches_for_user),
        ("renew_google_watches", renew_google_watches),
        ("setup_youtube_watches", setup_youtube_watches),
    ]

    success = True
    for name, task in tasks:
        try:
            # Check task is callable
            assert callable(task), f"{name} is not callable"
            print(f"✅ Task registered: {name}")
        except Exception as e:
            print(f"❌ Task {name} failed: {e}")
            success = False

    return success


def test_routes():
    """Test webhook URLs are configured"""
    print("\n🧪 Testing Webhook Routes...")

    from django.urls import reverse

    routes = [
        ("gmail-webhook", "/webhooks/gmail/"),
        ("calendar-webhook", "/webhooks/calendar/"),
        ("youtube-webhook", "/webhooks/youtube/"),
    ]

    success = True
    for name, expected_path in routes:
        try:
            url = reverse(name)
            if url == expected_path:
                print(f"✅ Route {name}: {url}")
            else:
                print(f"⚠️  Route {name}: {url} (expected {expected_path})")
        except Exception as e:
            print(f"❌ Route {name} not found: {e}")
            success = False

    return success


def test_helpers():
    """Test helper functions are importable"""
    print("\n🧪 Testing Helper Functions...")

    try:
        from automations.helpers.google_webhook_helper import (
            create_gmail_watch,
            stop_gmail_watch,
            create_calendar_watch,
            stop_calendar_watch,
            create_youtube_watch,
            renew_youtube_watch,
        )

        helpers = [
            "create_gmail_watch",
            "stop_gmail_watch",
            "create_calendar_watch",
            "stop_calendar_watch",
            "create_youtube_watch",
            "renew_youtube_watch",
        ]

        for helper in helpers:
            print(f"✅ Helper imported: {helper}")

        return True

    except ImportError as e:
        print(f"❌ Helper import failed: {e}")
        return False


def test_views():
    """Test webhook views are importable"""
    print("\n🧪 Testing Webhook Views...")

    try:
        from automations.google_webhook_views import (
            gmail_webhook,
            calendar_webhook,
            youtube_webhook,
        )

        views = [
            "gmail_webhook",
            "calendar_webhook",
            "youtube_webhook",
        ]

        for view in views:
            print(f"✅ View imported: {view}")

        return True

    except ImportError as e:
        print(f"❌ View import failed: {e}")
        return False


def test_configuration():
    """Test Django settings"""
    print("\n🧪 Testing Configuration...")

    from django.conf import settings

    configs = [
        ("GMAIL_WEBHOOK_ENABLED", False),
        ("CALENDAR_WEBHOOK_ENABLED", False),
        ("YOUTUBE_WEBHOOK_ENABLED", False),
        ("GMAIL_WEBHOOK_URL", None),
        ("CALENDAR_WEBHOOK_URL", None),
        ("YOUTUBE_WEBHOOK_URL", None),
    ]

    for key, default in configs:
        value = getattr(settings, key, default)
        status = "✅" if value else "⚠️ "
        print(f"{status} {key}: {value}")

    return True


def show_active_watches():
    """Display active watches"""
    print("\n📊 Active Google Watches:")

    watches = GoogleWebhookWatch.objects.select_related("user").all()

    if not watches:
        print("   No active watches")
        return

    for watch in watches:
        expiring = watch.is_expiring_soon(hours=24)
        status = "⏰ EXPIRING SOON" if expiring else "✅ Active"
        print(f"   {status} | {watch.user.username} | {watch.service} | "
              f"expires {watch.expiration.strftime('%Y-%m-%d %H:%M')}")


def show_youtube_areas():
    """Display active YouTube areas"""
    print("\n📊 Active YouTube Areas:")

    areas = Area.objects.filter(
        status=Area.Status.ACTIVE, action__name="youtube_new_video"
    ).select_related("owner", "action")

    if not areas:
        print("   No active YouTube areas")
        return

    channels = {}
    for area in areas:
        channel_id = area.action_config.get("channel_id", "N/A")
        if channel_id not in channels:
            channels[channel_id] = []
        channels[channel_id].append(area)

    for channel_id, areas_list in channels.items():
        print(f"   📺 Channel {channel_id}: {len(areas_list)} areas")


def main():
    print("=" * 70)
    print("🧪 Google Webhooks Infrastructure Test")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Model", test_model()))
    results.append(("Tasks", test_tasks()))
    results.append(("Routes", test_routes()))
    results.append(("Helpers", test_helpers()))
    results.append(("Views", test_views()))
    results.append(("Configuration", test_configuration()))

    # Show data
    show_active_watches()
    show_youtube_areas()

    # Summary
    print("\n" + "=" * 70)
    print("📋 Test Summary:")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("✅ All tests passed! Infrastructure ready.")
        print("\n📝 Next steps:")
        print("   1. Deploy to production: ./deployment/manage.sh update")
        print("   2. Verify domain on Google Search Console (required for Gmail)")
        print("   3. Test with real events (send email, create calendar event, upload video)")
        return 0
    else:
        print("❌ Some tests failed. Fix errors before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
