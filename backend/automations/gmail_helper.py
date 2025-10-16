##
## EPITECH PROJECT, 2025
## Area
## File description:
## gmail_helper
##

"""Gmail API helper functions for actions and reactions."""

import base64
import logging
from email.mime.text import MIMEText
from typing import Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def get_gmail_service(access_token: str):
    """
    Build Gmail API service from access token.

    Args:
        access_token: Valid Google OAuth2 access token

    Returns:
        Gmail API service resource
    """
    creds = Credentials(token=access_token)
    return build("gmail", "v1", credentials=creds)


def list_messages(
    access_token: str, query: str = "", max_results: int = 10
) -> List[Dict]:
    """
    List Gmail messages matching query.

    Args:
        access_token: Valid Google OAuth token
        query: Gmail search query (e.g., 'from:john@example.com is:unread')
               See: https://support.google.com/mail/answer/7190
        max_results: Max messages to return (default: 10)

    Returns:
        List of message dicts with id, threadId

    Raises:
        HttpError: If Gmail API request fails
    """
    try:
        service = get_gmail_service(access_token)
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        messages = results.get("messages", [])
        logger.info(f"Found {len(messages)} Gmail messages for query: '{query}'")
        return messages

    except HttpError as e:
        logger.error(f"Gmail list_messages failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in list_messages: {e}")
        raise


def get_message_details(access_token: str, message_id: str) -> Dict:
    """
    Get full message details including headers and body.

    Args:
        access_token: Valid Google OAuth token
        message_id: Gmail message ID

    Returns:
        Dict with parsed message details:
        - id: Message ID
        - thread_id: Thread ID
        - subject: Email subject
        - from: Sender email
        - to: Recipient email
        - date: Date header
        - snippet: Short preview text
        - labels: List of label IDs

    Raises:
        HttpError: If Gmail API request fails
    """
    try:
        service = get_gmail_service(access_token)
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        # Parse headers
        headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

        return {
            "id": message["id"],
            "thread_id": message["threadId"],
            "subject": headers.get("Subject", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "date": headers.get("Date", ""),
            "snippet": message.get("snippet", ""),
            "labels": message.get("labelIds", []),
        }

    except HttpError as e:
        logger.error(f"Gmail get_message_details failed for {message_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_message_details: {e}")
        raise


def send_email(access_token: str, to: str, subject: str, body: str) -> Dict:
    """
    Send email via Gmail API.

    Args:
        access_token: Valid Google OAuth token
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)

    Returns:
        Dict with message ID and threadId

    Raises:
        HttpError: If Gmail API request fails
        ValueError: If required parameters are missing
    """
    if not to:
        raise ValueError("Recipient email 'to' is required")

    try:
        service = get_gmail_service(access_token)

        # Create MIME message
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send message
        result = (
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
        )

        logger.info(f"Sent Gmail message: {result['id']} to {to}")
        return result

    except HttpError as e:
        logger.error(f"Gmail send_email failed to {to}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {e}")
        raise


def mark_message_read(access_token: str, message_id: str) -> Dict:
    """
    Mark a Gmail message as read.

    Args:
        access_token: Valid Google OAuth token
        message_id: Gmail message ID to mark as read

    Returns:
        Dict with updated message info

    Raises:
        HttpError: If Gmail API request fails
    """
    try:
        service = get_gmail_service(access_token)

        # Remove UNREAD label
        result = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
            .execute()
        )

        logger.info(f"Marked Gmail message {message_id} as read")
        return result

    except HttpError as e:
        logger.error(f"Gmail mark_message_read failed for {message_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in mark_message_read: {e}")
        raise


def add_label_to_message(access_token: str, message_id: str, label_name: str) -> Dict:
    """
    Add a label to a Gmail message (creates label if it doesn't exist).

    Args:
        access_token: Valid Google OAuth token
        message_id: Gmail message ID
        label_name: Name of the label to add

    Returns:
        Dict with updated message info

    Raises:
        HttpError: If Gmail API request fails
    """
    try:
        service = get_gmail_service(access_token)

        # Get or create label
        labels_result = service.users().labels().list(userId="me").execute()
        labels = labels_result.get("labels", [])

        label_id = next(
            (label["id"] for label in labels if label["name"] == label_name), None
        )

        if not label_id:
            # Create label if doesn't exist
            logger.info(f"Creating new Gmail label: {label_name}")
            label_body = {"name": label_name, "labelListVisibility": "labelShow"}
            new_label = (
                service.users().labels().create(userId="me", body=label_body).execute()
            )
            label_id = new_label["id"]

        # Add label to message
        result = (
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": [label_id]})
            .execute()
        )

        logger.info(f"Added label '{label_name}' to Gmail message {message_id}")
        return result

    except HttpError as e:
        logger.error(
            f"Gmail add_label_to_message failed for {message_id}, label {label_name}: {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_label_to_message: {e}")
        raise


def get_labels(access_token: str) -> List[Dict]:
    """
    Get all Gmail labels for the user.

    Args:
        access_token: Valid Google OAuth token

    Returns:
        List of label dicts with id, name, type

    Raises:
        HttpError: If Gmail API request fails
    """
    try:
        service = get_gmail_service(access_token)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        logger.info(f"Retrieved {len(labels)} Gmail labels")
        return labels

    except HttpError as e:
        logger.error(f"Gmail get_labels failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_labels: {e}")
        raise
