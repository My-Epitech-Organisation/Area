#!/usr/bin/env python3
"""
Test script to simulate a Twitch EventSub webhook notification.

Usage:
    python test_twitch_webhook.py [--event-type stream.online] [--broadcaster-id 123]
"""

import argparse
import hashlib
import hmac
import json
import time
import requests


def generate_twitch_signature(message_id: str, timestamp: str, body: bytes, secret: str) -> str:
    """Generate Twitch EventSub HMAC signature."""
    message = message_id.encode() + timestamp.encode() + body
    signature = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def send_test_webhook(
    webhook_url: str,
    secret: str,
    event_type: str = "stream.online",
    broadcaster_id: str = "123456789",
    broadcaster_login: str = "testuser"
):
    """Send a test Twitch EventSub webhook."""

    # Generate test data
    message_id = f"test-{int(time.time())}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Event payload based on type
    if event_type == "stream.online":
        event_data = {
            "broadcaster_user_id": broadcaster_id,
            "broadcaster_user_login": broadcaster_login,
            "broadcaster_user_name": broadcaster_login.capitalize(),
            "type": "live",
            "started_at": timestamp
        }
    elif event_type == "stream.offline":
        event_data = {
            "broadcaster_user_id": broadcaster_id,
            "broadcaster_user_login": broadcaster_login,
            "broadcaster_user_name": broadcaster_login.capitalize()
        }
    elif event_type == "channel.update":
        event_data = {
            "broadcaster_user_id": broadcaster_id,
            "broadcaster_user_login": broadcaster_login,
            "broadcaster_user_name": broadcaster_login.capitalize(),
            "title": "Test Stream Title",
            "language": "en",
            "category_id": "12345",
            "category_name": "Just Chatting",
            "content_classification_labels": []
        }
    else:
        event_data = {
            "broadcaster_user_id": broadcaster_id,
            "broadcaster_user_login": broadcaster_login,
        }

    # Full payload
    payload = {
        "subscription": {
            "id": "test-subscription-id",
            "status": "enabled",
            "type": event_type,
            "version": "1",
            "condition": {
                "broadcaster_user_id": broadcaster_id
            },
            "transport": {
                "method": "webhook",
                "callback": webhook_url
            },
            "created_at": timestamp
        },
        "event": event_data
    }

    # Convert to JSON
    body = json.dumps(payload).encode()

    # Generate signature
    signature = generate_twitch_signature(message_id, timestamp, body, secret)

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Twitch-Eventsub-Message-Id": message_id,
        "Twitch-Eventsub-Message-Timestamp": timestamp,
        "Twitch-Eventsub-Message-Signature": signature,
        "Twitch-Eventsub-Message-Type": "notification",
        "Twitch-Eventsub-Subscription-Type": event_type,
        "Twitch-Eventsub-Subscription-Version": "1"
    }

    print(f"Sending test webhook to {webhook_url}")
    print(f"Event type: {event_type}")
    print(f"Broadcaster: {broadcaster_login} (ID: {broadcaster_id})")
    print(f"Message ID: {message_id}")
    print(f"Timestamp: {timestamp}")
    print(f"\nPayload:\n{json.dumps(payload, indent=2)}")
    print(f"\nHeaders:\n{json.dumps(headers, indent=2)}")

    # Send request
    try:
        response = requests.post(
            webhook_url,
            headers=headers,
            data=body,
            timeout=10
        )

        print(f"\n{'='*60}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:\n{response.text}")
        print(f"{'='*60}")

        if response.status_code == 200:
            print("\n✅ Webhook sent successfully!")
        else:
            print(f"\n❌ Webhook failed with status {response.status_code}")

    except Exception as e:
        print(f"\n❌ Error sending webhook: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Test Twitch EventSub webhook notifications"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8080/webhooks/twitch/",
        help="Webhook URL (default: http://localhost:8080/webhooks/twitch/)"
    )
    parser.add_argument(
        "--secret",
        required=True,
        help="Webhook secret (WEBHOOK_SECRETS['twitch'])"
    )
    parser.add_argument(
        "--event-type",
        default="stream.online",
        choices=["stream.online", "stream.offline", "channel.update", "channel.follow", "channel.subscribe"],
        help="Event type to simulate (default: stream.online)"
    )
    parser.add_argument(
        "--broadcaster-id",
        default="123456789",
        help="Broadcaster user ID (default: 123456789)"
    )
    parser.add_argument(
        "--broadcaster-login",
        default="testuser",
        help="Broadcaster login name (default: testuser)"
    )

    args = parser.parse_args()

    send_test_webhook(
        webhook_url=args.url,
        secret=args.secret,
        event_type=args.event_type,
        broadcaster_id=args.broadcaster_id,
        broadcaster_login=args.broadcaster_login
    )


if __name__ == "__main__":
    main()
