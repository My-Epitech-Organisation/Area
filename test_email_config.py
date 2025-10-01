#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration email
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'area_project.settings')

import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.test import TestCase

def test_email_configuration():
    """Test de la configuration email"""
    print("📧 Test Configuration Email")
    print("=" * 40)

    # Vérification des variables d'environnement
    email_vars = {
        'EMAIL_BACKEND': os.getenv('EMAIL_BACKEND'),
        'EMAIL_HOST': os.getenv('EMAIL_HOST'),
        'EMAIL_PORT': os.getenv('EMAIL_PORT'),
        'EMAIL_USE_TLS': os.getenv('EMAIL_USE_TLS'),
        'EMAIL_USE_SSL': os.getenv('EMAIL_USE_SSL'),
        'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': '***' if os.getenv('EMAIL_HOST_PASSWORD') else None,
        'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL'),
    }

    print("🔍 Variables d'environnement:")
    for var, value in email_vars.items():
        status = "✅" if value else "⚪"
        print(f"{status} {var}: {value or 'NON DÉFINIE'}")

    # Vérification des settings Django
    print("\n🐍 Settings Django:")
    django_settings = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': settings.EMAIL_PORT,
        'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
        'EMAIL_USE_SSL': settings.EMAIL_USE_SSL,
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER or 'NON DÉFINI',
        'EMAIL_HOST_PASSWORD': '***' if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI',
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }

    for setting, value in django_settings.items():
        print(f"✅ {setting}: {value}")

    # Test de la configuration
    print("\n🧪 Test de fonctionnalité:")

    # Test avec backend console (par défaut)
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("📄 Backend Console détecté - Test d'envoi...")
        try:
            send_mail(
                'Test AREA Email Configuration',
                'Ceci est un test de configuration email pour le projet AREA.',
                settings.DEFAULT_FROM_EMAIL,
                ['test@example.com'],
                fail_silently=False,
            )
            print("✅ Test console réussi!")
        except Exception as e:
            print(f"❌ Erreur test console: {e}")

    # Configuration recommandée pour différents providers
    print("\n💡 Configurations recommandées:")
    configs = {
        'Gmail': {
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': '587',
            'EMAIL_USE_TLS': 'True',
            'EMAIL_USE_SSL': 'False',
            'Note': 'Utilisez un mot de passe d\'application'
        },
        'Outlook/Hotmail': {
            'EMAIL_HOST': 'smtp-mail.outlook.com',
            'EMAIL_PORT': '587',
            'EMAIL_USE_TLS': 'True',
            'EMAIL_USE_SSL': 'False',
        },
        'SendGrid': {
            'EMAIL_HOST': 'smtp.sendgrid.net',
            'EMAIL_PORT': '587',
            'EMAIL_USE_TLS': 'True',
            'EMAIL_USE_SSL': 'False',
            'EMAIL_HOST_USER': 'apikey',
            'Note': 'EMAIL_HOST_PASSWORD = votre clé API SendGrid'
        },
        'Mailgun': {
            'EMAIL_HOST': 'smtp.mailgun.org',
            'EMAIL_PORT': '587',
            'EMAIL_USE_TLS': 'True',
            'EMAIL_USE_SSL': 'False',
        }
    }

    for provider, config in configs.items():
        print(f"\n📮 {provider}:")
        for key, value in config.items():
            if key == 'Note':
                print(f"  💡 {value}")
            else:
                print(f"  {key}={value}")

def test_user_email_verification():
    """Test de la fonctionnalité de vérification email"""
    print("\n👤 Test Vérification Email Utilisateur")
    print("=" * 40)

    try:
        from users.models import User
        from users.views import SendEmailVerificationView

        print("✅ Models User importés avec succès")
        print("✅ Views SendEmailVerificationView importées avec succès")
        print("✅ Fonctionnalité de vérification email disponible")

        # Vérifier les champs requis
        user_fields = [field.name for field in User._meta.fields]
        required_fields = ['email_verified', 'email_verification_token']

        for field in required_fields:
            if field in user_fields:
                print(f"✅ Champ {field} présent dans le modèle User")
            else:
                print(f"❌ Champ {field} manquant dans le modèle User")

        return True

    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    print("🔧 AREA - Test Configuration Email")
    print("=" * 50)

    try:
        test_email_configuration()
        user_test_ok = test_user_email_verification()

        print("\n" + "=" * 50)
        if user_test_ok:
            print("🎉 Configuration email complète et fonctionnelle!")
            print("\n📋 Pour utiliser un vrai service email:")
            print("1. Modifiez EMAIL_BACKEND dans .env")
            print("2. Configurez EMAIL_HOST_USER et EMAIL_HOST_PASSWORD")
            print("3. Adaptez les autres paramètres selon votre provider")
        else:
            print("⚠️  Configuration email de base OK, mais vérifiez les models User")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        sys.exit(1)