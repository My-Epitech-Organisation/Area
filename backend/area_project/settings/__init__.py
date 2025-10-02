"""
Django settings auto-loader for AREA project.

This module automatically selects the appropriate settings based on the environment:
- local: Local development with SQLite/optional PostgreSQL
- docker: Docker environment with PostgreSQL and Redis
- production: Production environment (same as docker but with security settings)

Environment detection:
1. Check DJANGO_SETTINGS_MODULE environment variable
2. Check ENVIRONMENT environment variable
3. Check if running in Docker (/.dockerenv exists)
4. Default to local development
"""

import os
from pathlib import Path

# Detect environment
environment = os.getenv('ENVIRONMENT', '').lower()
django_settings = os.getenv('DJANGO_SETTINGS_MODULE', '')
is_docker = os.path.exists('/.dockerenv')

# Determine which settings to use
if 'docker' in django_settings or environment == 'docker' or is_docker:
    print(f"Loading Docker settings (detected: docker={is_docker}, env={environment})")
    from .docker import *  # noqa
elif 'local' in django_settings or environment == 'local' or environment == 'development':
    print(f"Loading Local settings (detected: env={environment})")
    from .local import *  # noqa
elif environment == 'production' or environment == 'prod':
    print(f"Loading Production settings (detected: env={environment})")
    from .docker import *  # noqa
    # Override with production-specific settings
    DEBUG = False
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
else:
    # Default to local development
    print(f"Loading Local settings (default, detected: env={environment})")
    from .local import *  # noqa

# Print configuration summary
try:
    print(f"Settings loaded:")
    print(f"  - DEBUG: {globals().get('DEBUG', 'Unknown')}")
    db_engine = globals().get('DATABASES', {}).get('default', {}).get('ENGINE', 'Unknown')
    if db_engine != 'Unknown':
        db_engine = db_engine.split('.')[-1]
    print(f"  - Database: {db_engine}")
    cache_backend = globals().get('CACHES', {}).get('default', {}).get('BACKEND', 'default')
    print(f"  - Cache backend: {cache_backend}")
    log_handlers = list(globals().get('LOGGING', {}).get('handlers', {}).keys())
    print(f"  - Log handlers: {log_handlers}")
    print(f"  - Environment: {environment or 'local (default)'}")
except Exception as e:
    print(f"Settings loaded with configuration summary error: {e}")