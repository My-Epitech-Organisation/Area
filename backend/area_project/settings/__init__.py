"""
Django settings auto-loader for AREA project.

This module automatically selects the appropriate settings based on the environment:
- local      : Local development with SQLite/optional PostgreSQL (venv outside Docker)
- docker     : Docker development with PostgreSQL, Redis, and hot reload (DEBUG=True)
- production : Production deployment with strict security, HTTPS, and optimizations (DEBUG=False)

Environment detection priority:
1. ENVIRONMENT variable (highest priority): "local", "docker", or "production"
2. /.dockerenv file existence (Docker container detection)
3. Default to local development (fallback)

Usage:
  Local dev:   export ENVIRONMENT=local && python manage.py runserver
  Docker dev:  docker-compose up (ENVIRONMENT=docker in .env)
  Production:  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
               (ENVIRONMENT=production in .env.production)

Accepted ENVIRONMENT values:
  - "local"      → loads local.py      (venv, SQLite)
  - "docker"     → loads docker_dev.py (Docker dev, PostgreSQL)
  - "production" → loads production.py (Docker prod, security hardened)
"""

import os
import sys
from pathlib import Path


def validate_critical_settings():
    """Validate that critical settings are properly configured."""
    errors = []
    warnings = []

    # Check SECRET_KEY
    secret_key = globals().get("SECRET_KEY", "")
    if not secret_key or secret_key == "your-secret-key-here":
        errors.append("SECRET_KEY is not set or using default value")

    # Check DEBUG mode in production
    debug = globals().get("DEBUG", False)
    environment = os.getenv("ENVIRONMENT", "").lower()
    if environment == "production" and debug:
        errors.append("DEBUG=True is not allowed in production")

    # Check ALLOWED_HOSTS in production
    if environment == "production":
        allowed_hosts = globals().get("ALLOWED_HOSTS", [])
        if not allowed_hosts or "*" in allowed_hosts:
            errors.append("ALLOWED_HOSTS must be properly configured in production (no wildcards)")

    # Check FRONTEND_URL
    frontend_url = globals().get("FRONTEND_URL", "")
    if not frontend_url:
        warnings.append("FRONTEND_URL is not set (OAuth redirects may fail)")

    # Check database configuration
    databases = globals().get("DATABASES", {})
    if not databases or "default" not in databases:
        errors.append("DATABASES configuration is missing or invalid")

    return errors, warnings


def print_configuration_summary(environment: str, settings_module: str):
    """Print a detailed summary of loaded settings."""
    try:
        print("\n" + "=" * 70)
        print(f"🚀 Django Settings Loaded: {settings_module}")
        print("=" * 70)

        # Environment info
        print(f"📍 Environment: {environment or 'local (default)'}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"🔧 DEBUG mode: {globals().get('DEBUG', 'Unknown')}")

        # Database info
        db_config = globals().get("DATABASES", {}).get("default", {})
        db_engine = db_config.get("ENGINE", "Unknown")
        if db_engine != "Unknown":
            db_engine = db_engine.split(".")[-1]
            db_name = db_config.get("NAME", "Unknown")
            db_host = db_config.get("HOST", "localhost")
            print(f"💾 Database: {db_engine} ({db_name} @ {db_host})")
        else:
            print(f"💾 Database: {db_engine}")

        # Cache info
        cache_backend = globals().get("CACHES", {}).get("default", {}).get("BACKEND", "default")
        if "redis" in cache_backend.lower():
            print(f"⚡ Cache: Redis")
        else:
            print(f"⚡ Cache: {cache_backend.split('.')[-1] if cache_backend != 'default' else 'Local memory'}")

        # Celery info
        celery_broker = globals().get("CELERY_BROKER_URL", "")
        if celery_broker:
            broker_type = "Redis" if "redis" in celery_broker else "Other"
            print(f"📨 Celery broker: {broker_type}")

        # Security info
        ssl_redirect = globals().get("SECURE_SSL_REDIRECT", False)
        secure_cookies = globals().get("SESSION_COOKIE_SECURE", False)
        cors_all = globals().get("CORS_ALLOW_ALL_ORIGINS", False)
        print(f"🔒 Security: SSL={'✓' if ssl_redirect else '✗'}, SecureCookies={'✓' if secure_cookies else '✗'}, CORS={'OPEN' if cors_all else 'RESTRICTED'}")

        # Logging info
        log_handlers = list(globals().get("LOGGING", {}).get("handlers", {}).keys())
        print(f"📝 Log handlers: {', '.join(log_handlers) if log_handlers else 'console (default)'}")

        # Frontend integration
        frontend_url = globals().get("FRONTEND_URL", "Not set")
        print(f"🌐 Frontend URL: {frontend_url}")

        # Validation
        errors, warnings = validate_critical_settings()

        if errors:
            print("\n❌ CRITICAL ERRORS:")
            for error in errors:
                print(f"   - {error}")
            print("\n⚠️  Application may not work correctly with these errors!")

        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")

        if not errors and not warnings:
            print("\n✅ All critical settings validated successfully")

        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n⚠️  Configuration summary error: {e}\n")


# =============================================================================
# ENVIRONMENT DETECTION & SETTINGS LOADING
# =============================================================================

# Get environment from variable (normalize to lowercase)
ENVIRONMENT = os.getenv("ENVIRONMENT", "").lower().strip()

# Check for Docker container
IS_DOCKER = os.path.exists("/.dockerenv")

# Determine which settings module to load
if ENVIRONMENT == "production":
    # Production environment - strict security, no debug
    print("🔴 Loading PRODUCTION settings...")
    try:
        from .production import *  # noqa: F401, F403
        LOADED_SETTINGS = "production"
    except ImportError as e:
        print(f"⚠️  Production settings not found: {e}")
        print("   Falling back to docker_dev settings with production overrides...")
        from .docker_dev import *  # noqa: F401, F403
        LOADED_SETTINGS = "docker_dev (production mode)"
        # Apply production overrides
        DEBUG = False
        if not os.getenv("ALLOWED_HOSTS"):
            print("❌ ERROR: ALLOWED_HOSTS must be set in production!")

elif ENVIRONMENT == "docker" or (IS_DOCKER and ENVIRONMENT not in ["local", "production"]):
    # Docker development environment
    print("🐳 Loading DOCKER development settings...")
    from .docker_dev import *  # noqa: F401, F403
    LOADED_SETTINGS = "docker_dev"

elif ENVIRONMENT == "local":
    # Explicit local development
    print("💻 Loading LOCAL development settings (venv)...")
    from .local import *  # noqa: F401, F403
    LOADED_SETTINGS = "local"

else:
    # Default: Auto-detect based on Docker presence
    if IS_DOCKER:
        print("🐳 Auto-detected Docker environment, loading docker_dev settings...")
        from .docker_dev import *  # noqa: F401, F403
        LOADED_SETTINGS = "docker_dev (auto-detected)"
    else:
        print("💻 Auto-detected local environment, loading local settings...")
        from .local import *  # noqa: F401, F403
        LOADED_SETTINGS = "local (auto-detected)"

# Print detailed configuration summary
print_configuration_summary(ENVIRONMENT or ("docker" if IS_DOCKER else "local"), LOADED_SETTINGS)

# Print detailed configuration summary
print_configuration_summary(ENVIRONMENT or ("docker" if IS_DOCKER else "local"), LOADED_SETTINGS)
