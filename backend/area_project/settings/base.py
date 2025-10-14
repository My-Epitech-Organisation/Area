"""
Base settings for AREA project.

This module contains common settings shared across all environments (local, docker, production).
Environment-specific settings (database, cache, security) should be defined in separate modules.

Structure:
    - Core Django settings (BASE_DIR, SECRET_KEY, INSTALLED_APPS, MIDDLEWARE)
    - Authentication & Security (AUTH_USER_MODEL, JWT, OAuth2)
    - Database (empty - defined per environment)
    - Static & Media files
    - REST Framework & API Documentation
    - Celery & Channels configuration
    - Logging configuration
    - Frontend integration (FRONTEND_URL, CORS)
    - Internationalization
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from django.core.exceptions import ImproperlyConfigured

# =============================================================================
# PATHS & ENVIRONMENT DETECTION
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # project root

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
IS_DOCKER = os.path.exists("/.dockerenv")

# Load environment variables from project root .env file
# In Docker, env vars are injected via docker-compose env_file
# In local dev, try to load from .env
if not IS_DOCKER:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try current directory
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print(f"Warning: .env file not found")

# Create logs directory
if not IS_DOCKER:
    LOGS_DIR = PROJECT_ROOT / "logs"
    LOGS_DIR.mkdir(exist_ok=True)
else:
    LOGS_DIR = Path("/app/logs")

# =============================================================================
# CORE DJANGO SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError:
    raise ImproperlyConfigured("Set the SECRET_KEY environment variable")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is overridden in environment-specific settings (local.py, docker.py, production.py)
DEBUG = os.getenv("DEBUG", "False") == "True"

# Installed Applications
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "channels",
    "django_celery_beat",
    # Local apps
    "users",
    "automations",
    # API documentation
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

# Middleware stack
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Must be before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL Configuration
ROOT_URLCONF = "area_project.urls"

# Template Configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI & ASGI Applications
WSGI_APPLICATION = "area_project.wsgi.application"
ASGI_APPLICATION = "area_project.routing.application"

# ALLOWED_HOSTS - overridden per environment
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================

# Custom user model
AUTH_USER_MODEL = "users.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY", SECRET_KEY),
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": (
        "rest_framework_simplejwt.authentication.default_user_authentication_rule"
    ),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# OAuth2 Provider Configuration
OAUTH2_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/google/callback"
        ),
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.readonly",
        ],
        "requires_refresh": True,
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv(
            "GITHUB_REDIRECT_URI", "http://localhost:8080/auth/oauth/github/callback/"
        ),
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
        "scopes": ["user", "repo", "notifications"],
        "requires_refresh": False,  # GitHub tokens don't expire
    },
}

# OAuth2 state expiry time (seconds)
OAUTH2_STATE_EXPIRY = 600  # 10 minutes

# Google Sign-In Configuration (for mobile apps)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Security Settings (base - extended per environment)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =============================================================================
# DATABASE
# =============================================================================

# Database configuration is environment-specific
# - local.py: SQLite (or optional PostgreSQL)
# - docker.py: PostgreSQL (Docker service)
# - production.py: PostgreSQL with connection pooling and tuning
DATABASES = {}  # Must be defined in environment-specific settings

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# =============================================================================
# REST FRAMEWORK & API DOCUMENTATION
# =============================================================================

# Django REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# API Documentation with drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "AREA API",
    "DESCRIPTION": "API documentation for the AREA project",
    "VERSION": "1.0.0",
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "AreaStatusEnum": "automations.models.Area.Status",
        "ServiceStatusEnum": "automations.models.Service.Status",
        "ExecutionStatusEnum": "automations.models.Execution.Status",
    },
}

# =============================================================================
# CELERY CONFIGURATION
# =============================================================================

# Celery broker and result backend (Redis)
# Overridden per environment for specific Redis configuration
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"  # Set after TIME_ZONE definition

# =============================================================================
# CHANNELS & WEBSOCKETS
# =============================================================================

# Channel layers for WebSocket support (Redis)
# Overridden per environment for specific configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379/0")],
        },
    },
}

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Email backend (console for dev, SMTP for production)
# Overridden per environment
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@areaction.app")

# =============================================================================
# FRONTEND INTEGRATION & CORS
# =============================================================================

# Frontend URL for OAuth redirects and CORS
# In development: http://localhost:5173 (Vite dev server)
# In production: https://your-frontend-domain.com
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS Configuration
# Base allowed origins (extended per environment)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# CORS_ALLOW_ALL_ORIGINS is set per environment (True for dev, False for prod)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "False") == "True"

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Adaptive logging configuration (extended per environment)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "area_project": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "automations": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "users": {
            "handlers": ["console"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Add file handler only if logs directory exists and is writable
try:
    if LOGS_DIR.exists() and os.access(LOGS_DIR, os.W_OK):
        LOGGING["handlers"]["file"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "django.log"),
            "formatter": "verbose",
        }
        # Add file handler to all loggers
        for logger in LOGGING["loggers"].values():
            if "file" not in logger["handlers"]:
                logger["handlers"].append("file")
        LOGGING["root"]["handlers"].append("file")
except Exception as e:
    print(f"Warning: Could not setup file logging: {e}")

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Update Celery timezone to match Django
CELERY_TIMEZONE = TIME_ZONE
