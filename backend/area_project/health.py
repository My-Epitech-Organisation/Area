"""Health check views for monitoring and Docker health checks."""

import time

from django.db import connections
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Docker and monitoring.
    Returns 200 if all services are healthy, 503 otherwise.
    """
    health_status = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "services": {},
    }

    # Check database connectivity
    try:
        db_conn = connections["default"]
        db_conn.cursor()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = f"unhealthy: {str(e)}"

    # Check Redis connectivity (if configured)
    try:
        import redis

        from django.conf import settings

        if hasattr(settings, "REDIS_URL"):
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unavailable: {str(e)}"

    # Return appropriate HTTP status
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)


@never_cache
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 when the application is ready to serve traffic.
    """
    return JsonResponse(
        {
            "status": "ready",
            "timestamp": int(time.time()),
        }
    )


@never_cache
@require_http_methods(["GET"])
def liveness_check(request):
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the application is alive.
    """
    return JsonResponse(
        {
            "status": "alive",
            "timestamp": int(time.time()),
        }
    )
