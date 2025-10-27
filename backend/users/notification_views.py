"""API views for user notifications."""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import OAuthNotification
from .notification_serializers import (
    OAuthNotificationSerializer,
    OAuthNotificationUpdateSerializer,
)
from .permissions import IsAuthenticatedAndVerified

logger = logging.getLogger(__name__)


class OAuthNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OAuth notifications.

    Provides endpoints for listing, retrieving, and updating user notifications
    about OAuth token issues.

    Endpoints:
        GET /api/notifications/ - List all notifications for current user
        GET /api/notifications/{id}/ - Get specific notification
        PATCH /api/notifications/{id}/ - Update notification (mark read/resolved)
        POST /api/notifications/mark_all_read/ - Mark all as read
        POST /api/notifications/mark_all_resolved/ - Mark all as resolved
        GET /api/notifications/unread_count/ - Get count of unread notifications
    """

    permission_classes = [IsAuthenticatedAndVerified]
    serializer_class = OAuthNotificationSerializer

    def get_queryset(self):
        """Get notifications for the current user only."""
        return OAuthNotification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ["update", "partial_update"]:
            return OAuthNotificationUpdateSerializer
        return OAuthNotificationSerializer

    def list(self, request, *args, **kwargs):
        """
        List OAuth notifications for the current user.

        Query Parameters:
            - is_read: Filter by read status (true/false)
            - is_resolved: Filter by resolved status (true/false)
            - service_name: Filter by service name

        Returns:
            List of notifications with pagination
        """
        queryset = self.get_queryset()

        # Apply filters from query parameters
        is_read = request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        is_resolved = request.query_params.get("is_resolved")
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == "true")

        service_name = request.query_params.get("service_name")
        if service_name:
            queryset = queryset.filter(service_name=service_name)

        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update a notification (mark as read/resolved).

        Only the owner of the notification can update it.
        """
        instance = self.get_object()

        # Ensure user owns this notification
        if instance.user != request.user:
            return Response(
                {"detail": "You do not have permission to modify this notification."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Mark all unread notifications as read for the current user.

        Returns:
            Number of notifications marked as read
        """
        count = OAuthNotification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)

        logger.info(
            f"User {request.user.username} marked {count} notifications as read"
        )

        return Response(
            {"message": f"{count} notifications marked as read", "count": count},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def mark_all_resolved(self, request):
        """
        Mark all unresolved notifications as resolved for the current user.

        Returns:
            Number of notifications marked as resolved
        """
        from django.utils import timezone

        count = OAuthNotification.objects.filter(
            user=request.user, is_resolved=False
        ).update(is_resolved=True, resolved_at=timezone.now())

        logger.info(
            f"User {request.user.username} marked {count} notifications as resolved"
        )

        return Response(
            {"message": f"{count} notifications marked as resolved", "count": count},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Get count of unread notifications for the current user.

        Returns:
            Count of unread notifications
        """
        count = OAuthNotification.objects.filter(
            user=request.user, is_read=False
        ).count()

        return Response({"count": count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def unresolved_count(self, request):
        """
        Get count of unresolved notifications for the current user.

        Returns:
            Count of unresolved notifications
        """
        count = OAuthNotification.objects.filter(
            user=request.user, is_resolved=False
        ).count()

        return Response({"count": count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        Mark a specific notification as read.

        Returns:
            Updated notification data
        """
        notification = self.get_object()

        if notification.user != request.user:
            return Response(
                {"detail": "You do not have permission to modify this notification."},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification.mark_read()
        serializer = self.get_serializer(notification)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_resolved(self, request, pk=None):
        """
        Mark a specific notification as resolved.

        Returns:
            Updated notification data
        """
        notification = self.get_object()

        if notification.user != request.user:
            return Response(
                {"detail": "You do not have permission to modify this notification."},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification.resolve()
        serializer = self.get_serializer(notification)

        return Response(serializer.data, status=status.HTTP_200_OK)
