"""
Docker development settings.

This module contains settings specific to Docker development environment.
Designed for docker-compose with volumes mounted for hot reload.

Usage:
  docker-compose up
  ENVIRONMENT=docker docker-compose up

Features:
  - PostgreSQL database (persistent, Docker service)
  - Redis for cache, Celery & Channels (Docker service)
  - DEBUG=True (can be toggled via environment variable)
  - File logging to /app/logs/ (persistent volume)
  - Hot reload via mounted volumes
  - Relaxed CORS for frontend development
  - Console email backend (emails in logs)
  - PostgreSQL connection pooling (60s)

Environment Variables:
  DEBUG=True|False        : Toggle debug mode (default: True)
  DB_HOST=db              : PostgreSQL host (Docker service name)
  REDIS_URL               : Redis connection string
  CORS_ALLOW_ALL_ORIGINS  : Allow all CORS origins (default: True)
  EMAIL_BACKEND           : Email backend (default: console)
  LOG_LEVEL               : Logging level (default: INFO)
"""

import os

from .base import *

# =============================================================================
# DEBUG & DEVELOPMENT MODE
# =============================================================================

# Can toggle debug in docker dev (default: True for development)
DEBUG = os.getenv("DEBUG", "True") == "True"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL - Docker service (persistent storage)
# Connection pooling enabled for better performance
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "area_db"),
        "USER": os.getenv("DB_USER", "area_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "area_password_2024"),
        "HOST": os.getenv("DB_HOST", "db"),  # Docker service name
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,  # Connection pooling (60 seconds)
        "OPTIONS": {
            "connect_timeout": 10,  # 10 seconds timeout
        },
    }
}

# =============================================================================
# REDIS & CELERY CONFIGURATION
# =============================================================================

# Redis - Docker service (shared for Celery, Channels, and optional caching)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# =============================================================================
# CHANNELS & WEBSOCKETS
# =============================================================================

# Channel layers with Redis for WebSocket support
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# =============================================================================
# CORS & FRONTEND INTEGRATION
# =============================================================================

# CORS for development - typically allow all origins
# Set CORS_ALLOW_ALL_ORIGINS=False in .env for more restrictive CORS
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True") == "True"

# If not allowing all origins, build allowed origins from ALLOWED_HOSTS
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        f"http://{host}:5173" for host in ALLOWED_HOSTS if host not in ["*", "0.0.0.0"]
    ] + [
        f"http://{host}:8081" for host in ALLOWED_HOSTS if host not in ["*", "0.0.0.0"]
    ]

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Email backend - default to console for development
# Can be overridden to SMTP for testing email functionality
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

# =============================================================================
# SECURITY SETTINGS (Disabled for Docker Dev)
# =============================================================================

# Allowed hosts for Docker (default: permissive for development)
# Override in .env for more restrictive settings
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# No SSL in docker dev (HTTP only)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# File logging in Docker container
# Logs written to /app/logs/ (should be mounted as volume for persistence)
if IS_DOCKER:
    try:
        os.makedirs("/app/logs", exist_ok=True)
        
        LOGGING["handlers"]["file"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "filename": "/app/logs/django.log",
            "formatter": "verbose",
        }
        
        # Add file handler to all loggers
        for logger in LOGGING["loggers"].values():
            if "file" not in logger["handlers"]:
                logger["handlers"].append("file")
        
        LOGGING["root"]["handlers"].append("file")
        
    except Exception as e:
        print(f"  ⚠ Warning: Could not setup file logging: {e}")

# =============================================================================
# CACHE CONFIGURATION (Optional for Docker Dev)
# =============================================================================

# For development, use local memory cache (faster, simpler)
# Production will use Redis cache
# Uncomment below to use Redis cache in development:
#
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }

# Print confirmation
print("✓ Docker development settings loaded")
