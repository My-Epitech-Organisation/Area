"""
API Views for the AREA automation system.

This module provides Django REST Framework ViewSets for:
- Service discovery (read-only)
- Action/Reaction discovery (read-only)
- Area CRUD operations with proper permissions and filtering
"""

import time
from typing import Any, Type

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Import django-filter if available, otherwise use basic filtering
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    # Fallback if django-filter is not installed
    DjangoFilterBackend = None

from .models import Action, Area, Execution, Reaction, Service
from .serializers import (
    AboutServiceSerializer,
    ActionSerializer,
    AreaCreateSerializer,
    AreaSerializer,
    ExecutionListSerializer,
    ExecutionSerializer,
    ExecutionStatsSerializer,
    ReactionSerializer,
    ServiceSerializer,
)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Service discovery - read-only operations.

    Provides list and retrieve operations for available services.
    Only shows active services by default.
    """

    queryset = Service.objects.filter(status=Service.Status.ACTIVE)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + (
        [DjangoFilterBackend] if DjangoFilterBackend else []
    )
    filterset_fields = ["status"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List all active services with caching."""
        return super().list(request, *args, **kwargs)


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Action discovery - read-only operations.

    Provides list and retrieve operations for available actions.
    Can be filtered by service.
    """

    queryset = Action.objects.select_related("service").filter(
        service__status=Service.Status.ACTIVE
    )
    serializer_class = ActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + (
        [DjangoFilterBackend] if DjangoFilterBackend else []
    )
    filterset_fields = ["service", "service__name"]
    search_fields = ["name", "description", "service__name"]
    ordering_fields = ["name", "service__name", "id"]
    ordering = ["service__name", "name"]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List all actions with caching."""
        return super().list(request, *args, **kwargs)


class ReactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Reaction discovery - read-only operations.

    Provides list and retrieve operations for available reactions.
    Can be filtered by service.
    """

    queryset = Reaction.objects.select_related("service").filter(
        service__status=Service.Status.ACTIVE
    )
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + (
        [DjangoFilterBackend] if DjangoFilterBackend else []
    )
    filterset_fields = ["service", "service__name"]
    search_fields = ["name", "description", "service__name"]
    ordering_fields = ["name", "service__name", "id"]
    ordering = ["service__name", "name"]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List all reactions with caching."""
        return super().list(request, *args, **kwargs)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an Area to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the Area
        return obj.owner == request.user


class AreaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Area CRUD operations with proper permissions.

    - Users can only see and modify their own Areas
    - Supports filtering by service, status, action, reaction
    - Supports search by name and description
    - Supports pagination
    """

    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + (
        [DjangoFilterBackend] if DjangoFilterBackend else []
    )
    filterset_fields = [
        "status",
        "action__service",
        "reaction__service",
        "action",
        "reaction",
    ]
    search_fields = [
        "name",
        "action__name",
        "reaction__name",
        "action__service__name",
        "reaction__service__name",
    ]
    ordering_fields = ["name", "created_at", "status"]
    ordering = ["-created_at"]  # Most recent first

    def get_queryset(self) -> QuerySet[Area]:  # type: ignore
        """
        Filter Areas to only show those owned by the current user.
        """
        return Area.objects.filter(owner=self.request.user).select_related(
            "action", "reaction", "action__service", "reaction__service"
        )

    def get_serializer_class(self) -> Type[Any]:
        """
        Use AreaCreateSerializer for create operations to get enhanced validation.
        """
        if self.action == "create":
            return AreaCreateSerializer
        return AreaSerializer

    def perform_create(self, serializer):
        """
        Set the owner to the current user when creating an Area.
        """
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """
        Custom action to toggle Area status between active/disabled.
        """
        area = self.get_object()

        if area.status == Area.Status.ACTIVE:
            area.status = Area.Status.DISABLED
        elif area.status == Area.Status.DISABLED:
            area.status = Area.Status.ACTIVE
        # PAUSED status requires explicit setting

        area.save()
        serializer = self.get_serializer(area)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        """
        Custom action to pause an Area.
        """
        area = self.get_object()
        area.status = Area.Status.PAUSED
        area.save()
        serializer = self.get_serializer(area)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        """
        Custom action to resume a paused Area.
        """
        area = self.get_object()
        if area.status == Area.Status.PAUSED:
            area.status = Area.Status.ACTIVE
            area.save()
        serializer = self.get_serializer(area)
        return Response(serializer.data)

    @action(detail=False)
    def stats(self, request):
        """
        Get statistics about user's Areas.
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "active": queryset.filter(status=Area.Status.ACTIVE).count(),
            "disabled": queryset.filter(status=Area.Status.DISABLED).count(),
            "paused": queryset.filter(status=Area.Status.PAUSED).count(),
            "by_service": {},
        }

        # Group by action service
        for area in queryset.select_related("action__service"):
            service_name = area.action.service.name
            if service_name not in stats["by_service"]:
                stats["by_service"][service_name] = 0
            stats["by_service"][service_name] += 1

        return Response(stats)


def about_json_view(request):
    """
    Return the /about.json endpoint for service discovery.

    This endpoint provides information about available services,
    actions, and reactions for client applications.
    """

    # Get all active services with their actions and reactions
    services = Service.objects.filter(status=Service.Status.ACTIVE).prefetch_related(
        "actions", "reactions"
    )

    serializer = AboutServiceSerializer(services, many=True)

    about_data = {
        "client": {"host": request.get_host()},
        "server": {
            "current_time": time.time(),
            "services": serializer.data,
        },
    }

    return JsonResponse(about_data)


class ExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Execution journaling and monitoring.

    Provides list and retrieve operations for execution history.
    Users can only view executions from their own Areas.

    Supports filtering by:
    - area: Filter by specific Area ID
    - status: Filter by execution status (pending, running, success, failed, skipped)
    - created_after: Filter executions created after this date (ISO format)
    - created_before: Filter executions created before this date (ISO format)

    Supports search on:
    - area name
    - external_event_id

    Supports ordering by:
    - created_at (default: most recent first)
    - started_at
    - completed_at
    - status
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + (
        [DjangoFilterBackend] if DjangoFilterBackend else []
    )
    filterset_fields = ["area", "status"]
    search_fields = ["area__name", "external_event_id"]
    ordering_fields = ["created_at", "started_at", "completed_at", "status"]
    ordering = ["-created_at"]  # Most recent first

    def get_queryset(self) -> QuerySet[Execution]:  # type: ignore
        """
        Filter Executions to only show those from Areas owned by the current user.
        Optimized with select_related to avoid N+1 queries.
        """
        queryset = Execution.objects.filter(
            area__owner=self.request.user
        ).select_related(
            "area",
            "area__action",
            "area__reaction",
            "area__action__service",
            "area__reaction__service",
        )

        # Date range filtering
        created_after = self.request.query_params.get("created_after")
        created_before = self.request.query_params.get("created_before")

        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)

        return queryset

    def get_serializer_class(self) -> Type[Any]:
        """
        Use ExecutionListSerializer for list views (optimized),
        ExecutionSerializer for detail views (full data).
        """
        if self.action == "list":
            return ExecutionListSerializer
        return ExecutionSerializer

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get statistics about user's executions.

        Returns:
        - total: Total number of executions
        - pending/running/success/failed/skipped: Count by status
        - by_area: Count grouped by area name
        - recent_failures: Last 10 failed executions
        """
        queryset = self.get_queryset()

        stats_data = {
            "total": queryset.count(),
            "pending": queryset.filter(status=Execution.Status.PENDING).count(),
            "running": queryset.filter(status=Execution.Status.RUNNING).count(),
            "success": queryset.filter(status=Execution.Status.SUCCESS).count(),
            "failed": queryset.filter(status=Execution.Status.FAILED).count(),
            "skipped": queryset.filter(status=Execution.Status.SKIPPED).count(),
            "by_area": {},
            "recent_failures": [],
        }

        # Group by area name
        for execution in queryset.select_related("area"):
            area_name = execution.area.name
            if area_name not in stats_data["by_area"]:
                stats_data["by_area"][area_name] = 0
            stats_data["by_area"][area_name] += 1

        # Get recent failures
        recent_failures = (
            queryset.filter(status=Execution.Status.FAILED)
            .order_by("-created_at")[:10]
            .select_related("area", "area__action", "area__reaction")
        )
        stats_data["recent_failures"] = ExecutionListSerializer(
            recent_failures, many=True
        ).data

        serializer = ExecutionStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-area/(?P<area_id>[^/.]+)")
    def by_area(self, request, area_id=None):
        """
        List executions for a specific area.

        URL: /executions/by-area/{area_id}/
        """
        # Verify the area belongs to the user
        try:
            area = Area.objects.get(id=area_id, owner=request.user)
        except Area.DoesNotExist:
            return Response(
                {"detail": "Area not found or access denied."},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = self.get_queryset().filter(area=area)

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ExecutionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ExecutionListSerializer(queryset, many=True)
        return Response(serializer.data)

