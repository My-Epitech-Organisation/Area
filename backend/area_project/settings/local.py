"""
Local development settings for AREA project.

This module contains settings specific to local development environment.
Use this for running tests, development server, and debugging.
"""

import os
import sys

from .base import *

# Override for local development
DEBUG = True

# Database for local development
# For tests, Django will automatically use SQLite in-memory database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "TEST": {
            "NAME": ":memory:",  # Use in-memory database for tests
        },
    }
}

# Override PostgreSQL only if explicitly requested
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
                "NAME": "test_area_db",
            },
        }
    }

# Local Redis (optional, fallback to in-memory for development)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Use local Redis if available, otherwise use in-memory channel layer
try:
    import redis

    r = redis.Redis.from_url(REDIS_URL)
    r.ping()  # type: ignore
    # Redis is available
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }
except Exception:
    # Fallback to in-memory channel layer for development
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }

# Development-specific settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Console email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Additional local settings
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# More permissive CORS for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]

# Disable some security features for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Development logging - more verbose
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "INFO",  # Set to DEBUG to see SQL queries
    "propagate": False,
}

# Test-specific settings
if "test" in sys.argv or "pytest" in sys.modules:
    # Use in-memory SQLite for tests
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

    # Disable migrations for faster tests
    MIGRATION_MODULES = {
        "users": None,
        "automations": None,
    }

    # Simpler password hashing for tests
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]

    # Disable logging during tests
    import logging

    logging.disable(logging.CRITICAL)
