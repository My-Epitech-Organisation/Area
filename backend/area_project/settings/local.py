"""
Local development settings - venv outside Docker.

This module contains settings specific to local development environment
running on the host machine (outside Docker containers).

Usage:
  python manage.py runserver
  ENVIRONMENT=local python manage.py runserver

Features:
  - SQLite database (fast, no setup needed, or optional PostgreSQL)
  - DEBUG=True (verbose error pages, hot reload)
  - Console email backend (emails printed to terminal)
  - Hot reload enabled (auto-restart on code changes)
  - CORS allow all origins (permissive for frontend dev)
  - No SSL/security restrictions (local HTTP only)
  - In-memory channel layer fallback (if Redis unavailable)
  - Verbose logging for debugging
  - Fast test configuration (in-memory DB, simple password hashing)

Environment Variables:
  USE_POSTGRES=True       : Use PostgreSQL instead of SQLite
  REDIS_URL               : Redis connection (optional, fallback to in-memory)
  DB_NAME, DB_USER, etc.  : PostgreSQL credentials (if USE_POSTGRES=True)
"""

import os
import sys

from .base import *

# =============================================================================
# DEBUG & DEVELOPMENT MODE
# =============================================================================

# Force debug mode for local development
DEBUG = True

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# SQLite for simplicity and speed (default)
# Ideal for local development, testing, and rapid prototyping
# No database server setup required
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TEST": {
            "NAME": ":memory:",  # Use in-memory database for tests (fast)
        },
    }
}

# Optional: PostgreSQL if user wants production-like database locally
# Set USE_POSTGRES=True in .env to enable PostgreSQL
# Useful for testing PostgreSQL-specific features (JSON fields, full-text search, etc.)
if os.getenv("USE_POSTGRES", "False") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "area_db"),
            "USER": os.getenv("DB_USER", "area_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "area_password_2024"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "TEST": {
                "NAME": "test_area_db",  # Separate test database
            },
        }
    }

# =============================================================================
# REDIS & CELERY CONFIGURATION
# =============================================================================

# Redis optional (fallback to in-memory if not available)
# Celery and Channels will use Redis if running, otherwise fallback gracefully
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# =============================================================================
# CHANNELS & WEBSOCKETS
# =============================================================================

# Use local Redis for WebSockets if available, otherwise use in-memory
# In-memory channel layer works fine for local dev with single process
try:
    import redis

    r = redis.Redis.from_url(REDIS_URL)
    r.ping()  # type: ignore
    # Redis is available - use it for channels
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }
    print("  ✓ Using Redis for channels")
except Exception:
    # Fallback to in-memory channel layer (works for single process)
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
    print("  ⚠ Using in-memory channel layer (Redis not available)")

# =============================================================================
# CORS & FRONTEND INTEGRATION
# =============================================================================

# Development CORS - allow everything for easy frontend testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Additional allowed origins (redundant with ALLOW_ALL, but explicit)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React dev server
    "http://localhost:5173",   # Vite dev server (default frontend)
    "http://localhost:8000",   # Django dev server
    "http://localhost:8080",   # Alternative frontend port
    "http://localhost:8081",   # Alternative frontend port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Console email backend - emails printed to terminal
# Perfect for development - see emails without SMTP setup
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# SECURITY SETTINGS (Disabled for Local Dev)
# =============================================================================

# Permissive hosts - accept any host for local development
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# No SSL in local dev (HTTP only)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable additional security filters for easier debugging
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Verbose logging for debugging
# Set django.db.backends to DEBUG to see SQL queries
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "INFO",  # Change to "DEBUG" to see all SQL queries
    "propagate": False,
}

# =============================================================================
# TEST-SPECIFIC SETTINGS
# =============================================================================

# Automatically detected when running tests
if "test" in sys.argv or "pytest" in sys.modules:
    print("  🧪 Test mode detected - optimizing for speed")

    # Use in-memory SQLite for tests (fastest)
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

    # Disable migrations for faster tests (use --nomigrations flag alternative)
    MIGRATION_MODULES = {
        "users": None,
        "automations": None,
    }

    # Simpler password hashing for tests (10x faster)
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]

    # Disable logging during tests (cleaner output)
    import logging

    logging.disable(logging.CRITICAL)

# Print confirmation
print("✓ Local development settings loaded (venv)")
