#!/usr/bin/env python
"""
Test email configuration for AREA project.

This script tests the email configuration by sending a test email.
Run from the backend directory:
    python manage.py shell < scripts/test_email.py
Or:
    python manage.py test_email
"""

import sys

from django.conf import settings
from django.core.mail import send_mail


def test_email_configuration():
    """Test email configuration by sending a test email."""

    print("\n" + "=" * 70)
    print("🔧 Testing Email Configuration")
    print("=" * 70)

    # Display current configuration
    print(f"\n📧 Email Backend: {settings.EMAIL_BACKEND}")

    if "smtp" in settings.EMAIL_BACKEND.lower():
        print(f"📧 SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        print(f"📧 SMTP Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        print(f"📧 SMTP User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        print(f"📧 Use TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        print(f"📧 Use SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")

    print(f"📧 From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")

    # Ask for test email
    print("\n" + "-" * 70)
    test_email = input("Enter test email address (or press Enter to skip): ").strip()

    if not test_email:
        print("❌ Test skipped - no email address provided")
        return False

    print(f"\n📤 Sending test email to: {test_email}")
    print("-" * 70)

    try:
        # Send test email
        subject = "AREA - Test Email"
        message = """
Hello,

This is a test email from the AREA platform.

If you received this email, your email configuration is working correctly!

Technical details:
- Backend: {}
- From: {}

Best regards,
The AREA Team
""".format(settings.EMAIL_BACKEND, settings.DEFAULT_FROM_EMAIL)

        html_message = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0;">✅ Email Test Successful!</h1>
    </div>

    <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px;">Hello,</p>

        <p style="font-size: 16px;">This is a test email from the <strong>AREA platform</strong>.</p>

        <div style="background-color: #fff; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; color: #22c55e; font-weight: bold; font-size: 18px;">
                ✓ Your email configuration is working correctly!
            </p>
        </div>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <p style="font-size: 14px; color: #666;">
            <strong>Technical Details:</strong><br>
            Backend: {}<br>
            From: {}
        </p>

        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            Best regards,<br>
            <strong>The AREA Team</strong>
        </p>
    </div>
</body>
</html>
""".format(settings.EMAIL_BACKEND, settings.DEFAULT_FROM_EMAIL)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            html_message=html_message,
            fail_silently=False,
        )

        print("\n✅ Test email sent successfully!")
        print("\nPlease check your inbox (and spam folder) for the test email.")
        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Error sending test email: {e}")
        print("\nPossible issues:")
        print("  1. Check SMTP credentials in .env file")
        print("  2. Verify EMAIL_HOST_PASSWORD is correct (use Gmail App Password)")
        print("  3. Check firewall/network settings")
        print("  4. Verify SMTP server is reachable")
        print("=" * 70 + "\n")
        return False


if __name__ == "__main__":
    # If run directly, execute test
    test_email_configuration()
else:
    # If imported in Django shell, just define the function
    print("Function 'test_email_configuration()' is available.")
    print("Run it with: test_email_configuration()")
