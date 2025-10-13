"""
Docker/Production settings for AREA project.

This module contains settings specific to Docker and production environments.
"""

import os

from .base import *

# Production settings
DEBUG = os.getenv("DEBUG", "False") == "True"

# Database - PostgreSQL for Docker/Production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "area_db"),
        "USER": os.getenv("DB_USER", "area_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "area_password_2024"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# Redis for Docker
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Channel layers with Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") == "True"
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        f"http://{host}:8081" for host in ALLOWED_HOSTS if host not in ["*", "0.0.0.0"]
    ] + [f"https://{host}" for host in ALLOWED_HOSTS if host not in ["*", "0.0.0.0"]]

# Email settings for production
if not DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
    )

# File logging for Docker
if LOGS_DIR.exists() or IS_DOCKER:
    try:
        # Ensure logs directory exists in Docker
        if IS_DOCKER:
            os.makedirs("/app/logs", exist_ok=True)
            log_file = "/app/logs/django.log"
        else:
            log_file = str(LOGS_DIR / "django.log")

        LOGGING["handlers"]["file"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "verbose",
        }

        # Add file handler to all loggers
        for logger_config in LOGGING["loggers"].values():
            if "file" not in logger_config["handlers"]:
                logger_config["handlers"].append("file")
        LOGGING["root"]["handlers"].append("file")

    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

# Static files handling for production
if not DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Cache configuration for production
if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

    # Use cache for sessions in production
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

# Development: Override logging to console-only to avoid SELinux permission issues
# with mounted volumes in Docker development environments
if os.getenv("ENVIRONMENT") == "development":
    LOGGING["root"]["handlers"] = ["console"]
    LOGGING["loggers"]["django"]["handlers"] = ["console"]
    # Only override celery logger if it exists
    if "celery" in LOGGING.get("loggers", {}):
        LOGGING["loggers"]["celery"]["handlers"] = ["console"]
