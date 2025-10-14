"""
Production settings for Docker deployment.

This module contains settings specific to production environment.
Designed for deployment with maximum security, performance, and reliability.

Usage:
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
  ENVIRONMENT=production docker-compose up

Features:
  - PostgreSQL database (persistent, tuned with connection pooling)
  - Redis for cache, sessions & Celery
  - DEBUG=False (strict, no debug information exposed)
  - HTTPS/SSL enforcement (all traffic redirected to HTTPS)
  - Secure cookies (HTTPS only, HttpOnly)
  - HSTS headers (HTTP Strict Transport Security)
  - Static files served by nginx (not Django)
  - Rotating file logs (separate error log)
  - Redis cache for sessions (faster, scalable)
  - Strict CORS (only trusted origins)
  - Comprehensive validation (fails fast on misconfiguration)

Environment Variables (REQUIRED):
  SECRET_KEY              : Strong secret key (min 50 chars, rotate regularly)
  JWT_SIGNING_KEY         : JWT signing key (different from SECRET_KEY)
  DB_NAME, DB_USER, etc.  : PostgreSQL credentials
  REDIS_URL               : Redis connection string
  FRONTEND_URL            : Frontend URL (for CORS and OAuth redirects)
  ALLOWED_HOSTS           : Comma-separated hostnames (NO wildcards!)
  EMAIL_HOST, etc.        : SMTP credentials for production email

Environment Variables (OPTIONAL):
  SECURE_SSL_REDIRECT     : Force HTTPS redirect (default: True)
  SECURE_HSTS_SECONDS     : HSTS max-age (default: 31536000 = 1 year)
  LOG_LEVEL               : Logging level (default: WARNING)
"""

import os

from .base import *

# =============================================================================
# DEBUG MODE (MUST be False in production)
# =============================================================================

# Production MUST be non-debug
# Debug mode exposes sensitive information and should NEVER be enabled in production
DEBUG = False

# =============================================================================
# DATABASE CONFIGURATION (Production-tuned PostgreSQL)
# =============================================================================

# PostgreSQL with production optimizations
# Connection pooling (600s = 10 minutes) for better performance
# Statement timeout (30s) prevents long-running queries from blocking
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,  # 10 minutes connection pooling
        "OPTIONS": {
            "connect_timeout": 10,  # 10 seconds connection timeout
            "options": "-c statement_timeout=30000",  # 30 seconds query timeout
        },
    }
}

# =============================================================================
# REDIS CONFIGURATION (Cache, Sessions, Celery, Channels)
# =============================================================================

# Redis for everything in production (cache, sessions, Celery, WebSockets)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Redis cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # 5 seconds
            "SOCKET_TIMEOUT": 5,  # 5 seconds
        },
        "KEY_PREFIX": "area",  # Prefix for cache keys
    }
}

# Use Redis cache for sessions (faster, scalable)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

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
# ALLOWED HOSTS & CORS (Strict validation)
# =============================================================================

# Strict hosts validation (NO wildcards allowed!)
allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "")
if not allowed_hosts_str:
    raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production")

ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_str.split(",") if h.strip()]

# Validate no wildcards in ALLOWED_HOSTS
if "*" in ALLOWED_HOSTS or "0.0.0.0" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Wildcards (*) or 0.0.0.0 are not allowed in production ALLOWED_HOSTS. "
        "Specify exact hostnames: 'api.example.com,example.com'"
    )

# CORS - strict origins only (no wildcard origins)
CORS_ALLOW_ALL_ORIGINS = False

# Frontend URL must be set for OAuth redirects
frontend_url = os.getenv("FRONTEND_URL")
if not frontend_url:
    raise ImproperlyConfigured(
        "FRONTEND_URL must be set in production for OAuth redirects and CORS"
    )

# Validate FRONTEND_URL is not using default localhost value
if "localhost" in frontend_url or "127.0.0.1" in frontend_url:
    print("⚠️  WARNING: FRONTEND_URL is using localhost in production")
    print(f"   Current: {frontend_url}")
    print("   This will not work for remote clients. Use your actual domain.")

# Build CORS allowed origins from FRONTEND_URL
CORS_ALLOWED_ORIGINS = [frontend_url]

# Add additional trusted origins if specified
additional_origins = os.getenv("CORS_ADDITIONAL_ORIGINS", "")
if additional_origins:
    CORS_ALLOWED_ORIGINS.extend(
        [origin.strip() for origin in additional_origins.split(",") if origin.strip()]
    )

# =============================================================================
# EMAIL CONFIGURATION (SMTP required in production)
# =============================================================================

# SMTP email backend in production (no console backend)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@areaction.app")

# Validate email configuration (warning only, not fatal)
if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    print("⚠️  WARNING: Email not fully configured in production")
    print("    Email notifications will not work until SMTP is configured")

# =============================================================================
# SECURITY SETTINGS (Maximum security for production)
# =============================================================================

# Force HTTPS redirection (all HTTP traffic redirected to HTTPS)
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Secure cookies (HTTPS only, not accessible via JavaScript)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Cookie age (2 weeks for session, 1 year for CSRF)
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
CSRF_COOKIE_AGE = 31536000  # 1 year in seconds

# Additional security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"  # Prevent clickjacking

# HSTS (HTTP Strict Transport Security)
# Tells browsers to only access the site via HTTPS for the next year
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy (optional but recommended)
# Uncomment and customize based on your needs:
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
# CSP_IMG_SRC = ("'self'", "data:", "https:")
# CSP_FONT_SRC = ("'self'", "https:")
# CSP_CONNECT_SRC = ("'self'",)

# =============================================================================
# LOGGING CONFIGURATION (Production - warnings and errors only)
# =============================================================================

# Ensure logs directory exists (only in Docker)
try:
    os.makedirs("/app/logs", exist_ok=True)
    logs_dir = "/app/logs"
except (PermissionError, OSError):
    # Fallback for testing outside Docker
    logs_dir = os.path.join(BASE_DIR.parent, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    print(f"⚠️  Using fallback logs directory: {logs_dir}")

# File logging with rotation (10MB max, keep 5 backups)
LOGGING["handlers"]["file"] = {
    "level": os.getenv("LOG_LEVEL", "WARNING"),
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(logs_dir, "django.log"),
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "backupCount": 5,
    "formatter": "verbose",
}

# Separate error log for critical issues
LOGGING["handlers"]["error_file"] = {
    "level": "ERROR",
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.path.join(logs_dir, "django_errors.log"),
    "maxBytes": 1024 * 1024 * 10,  # 10MB
    "backupCount": 5,
    "formatter": "verbose",
}

# Update all loggers to use file handlers
for logger in LOGGING["loggers"].values():
    logger["handlers"] = ["console", "file", "error_file"]
    logger["level"] = os.getenv("LOG_LEVEL", "WARNING")

LOGGING["root"]["handlers"] = ["console", "file", "error_file"]
LOGGING["root"]["level"] = os.getenv("LOG_LEVEL", "WARNING")

# =============================================================================
# STATIC & MEDIA FILES (Served by nginx in production)
# =============================================================================

# Static files collected to /app/staticfiles (served by nginx)
STATIC_ROOT = "/app/staticfiles"
MEDIA_ROOT = "/app/mediafiles"

# Static files storage with manifest for cache busting
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# =============================================================================
# PERFORMANCE OPTIMIZATIONS
# =============================================================================

# Template caching (only in production with DEBUG=False)
if not DEBUG:
    for template_engine in TEMPLATES:
        if (
            template_engine["BACKEND"]
            == "django.template.backends.django.DjangoTemplates"
        ):
            # Remove app_dirs when using cached loader
            if template_engine["APP_DIRS"]:
                template_engine["APP_DIRS"] = False

            # Set up cached loader
            template_engine["OPTIONS"]["loaders"] = [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ]

# =============================================================================
# VALIDATION (Fail fast on misconfiguration)
# =============================================================================

# Validate critical settings at startup
required_settings = {
    "SECRET_KEY": SECRET_KEY,
    "FRONTEND_URL": globals().get("FRONTEND_URL"),
    "ALLOWED_HOSTS": ALLOWED_HOSTS,
    "DB_NAME": os.getenv("DB_NAME"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
}

for name, value in required_settings.items():
    if not value:
        raise ImproperlyConfigured(
            f"{name} must be set in production. "
            f"Check your .env.production file and environment variables."
        )

# Validate SECRET_KEY strength (minimum 50 characters)
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "SECRET_KEY is too short. Use a strong secret key with at least 50 characters. "
        "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# Validate OAuth credentials (warning only)
oauth_providers = globals().get("OAUTH2_PROVIDERS", {})
for provider, config in oauth_providers.items():
    if not config.get("client_id") or not config.get("client_secret"):
        print(f"⚠️  WARNING: {provider} OAuth not configured")
        print(f"    OAuth authentication with {provider} will not work")

# Validate database connection (basic check)
db_host = os.getenv("DB_HOST", "db")
if db_host in ["localhost", "127.0.0.1"]:
    print("⚠️  WARNING: Database host is localhost/127.0.0.1")
    print("    This might not work in Docker. Use the service name (e.g., 'db')")

# Print success message
print("✅ Production settings loaded - All security checks passed")
print(f"   Allowed hosts: {', '.join(ALLOWED_HOSTS)}")
print(f"   Frontend URL: {frontend_url}")
print(f"   SSL redirect: {'Enabled' if SECURE_SSL_REDIRECT else 'Disabled'}")
print(f"   Debug mode: {'ENABLED (DANGER!)' if DEBUG else 'Disabled ✓'}")
