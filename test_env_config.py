#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration des variables d'environnement
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Variables d'environnement requises avec leurs valeurs par défaut
REQUIRED_VARS = {
    # Base de données
    'DB_USER': 'area_user',
    'DB_PASSWORD': 'area_password_2024',
    'DB_NAME': 'area_db',
    'DB_HOST': 'db',
    'DB_PORT': '5432',

    # Django
    'SECRET_KEY': 'your-very-secret-django-key-change-in-production',
    'DEBUG': 'True',
    'ALLOWED_HOSTS': 'localhost,127.0.0.1,0.0.0.0',

    # Redis
    'REDIS_URL': 'redis://redis:6379/0',
    'REDIS_PORT': '6379',

    # JWT
    'JWT_SIGNING_KEY': 'your-jwt-signing-key-change-in-production',

    # Ports
    'BACKEND_PORT': '8080',
    'FRONTEND_PORT': '8081',
    'FLOWER_PORT': '5555',

    # Email
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'True',
    'DEFAULT_FROM_EMAIL': 'noreply@area.com',

    # CORS
    'CORS_ALLOW_ALL_ORIGINS': 'True',

    # Logging
    'LOG_LEVEL': 'INFO',

    # Celery
    'CELERY_TIMEZONE': 'UTC',
    'CELERY_TASK_ALWAYS_EAGER': 'False',
}

# Variables optionnelles
OPTIONAL_VARS = {
    'EMAIL_HOST_USER': '',
    'EMAIL_HOST_PASSWORD': '',
    'GOOGLE_CLIENT_ID': '',
    'GOOGLE_CLIENT_SECRET': '',
    'GITHUB_CLIENT_ID': '',
    'GITHUB_CLIENT_SECRET': '',
    'DJANGO_LOG_FILE': '/app/logs/django.log',
}

def check_env_vars():
    """Vérifie que toutes les variables d'environnement sont définies"""
    missing_vars = []

    print("🔍 Vérification des variables d'environnement...")
    print("=" * 50)

    # Vérifier les variables requises
    for var, default in REQUIRED_VARS.items():
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
            print(f"❌ {var}: MANQUANTE (défaut: {default})")
        else:
            print(f"✅ {var}: {value}")

    # Afficher les variables optionnelles
    print("\n📋 Variables optionnelles:")
    print("-" * 30)
    for var, default in OPTIONAL_VARS.items():
        value = os.getenv(var, default)
        status = "✅" if value else "⚪"
        print(f"{status} {var}: {value if value else 'NON DÉFINIE'}")

    # Résumé
    print("\n" + "=" * 50)
    if missing_vars:
        print(f"❌ {len(missing_vars)} variable(s) manquante(s): {', '.join(missing_vars)}")
        print("💡 Copiez .env.example vers .env et adaptez les valeurs")
        return False
    else:
        print("✅ Toutes les variables requises sont définies!")
        return True

def test_django_settings():
    """Test de chargement des settings Django"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'area_project.settings')

        # Import django et configuration
        import django
        from django.conf import settings

        django.setup()

        print("\n🐍 Test Django Settings:")
        print("-" * 30)
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ SECRET_KEY: {'SET' if settings.SECRET_KEY else 'NOT SET'}")
        print(f"✅ DATABASES: {len(settings.DATABASES)} configurée(s)")
        print(f"✅ Redis URL: {settings.REDIS_URL}")
        print(f"✅ Celery Broker: {settings.CELERY_BROKER_URL}")

        return True
    except Exception as e:
        print(f"❌ Erreur Django settings: {e}")
        return False

if __name__ == "__main__":
    print("🔧 AREA - Test Configuration Variables d'Environnement")
    print("=" * 60)

    env_ok = check_env_vars()

    if env_ok:
        django_ok = test_django_settings()

        if django_ok:
            print("\n🎉 Configuration complète et fonctionnelle!")
            sys.exit(0)
        else:
            print("\n❌ Problème avec la configuration Django")
            sys.exit(1)
    else:
        print("\n❌ Variables d'environnement manquantes")
        sys.exit(1)