"""
Django management command to test email configuration.

Usage:
    python manage.py test_email recipient@example.com
"""

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """Test email configuration by sending a test email."""

    help = "Test email configuration by sending a test email"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "recipient",
            type=str,
            help="Email address to send test email to",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        recipient = options["recipient"]

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  AREA - Email Configuration Test"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        # Display configuration
        self.stdout.write(self.style.HTTP_INFO("📧 Configuration:"))
        self.stdout.write(f"  Backend: {settings.EMAIL_BACKEND}")

        if "smtp" in settings.EMAIL_BACKEND.lower():
            self.stdout.write(
                f"  SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}"
            )
            self.stdout.write(
                f"  SMTP Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}"
            )
            self.stdout.write(
                f"  SMTP User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}"
            )
            self.stdout.write(
                f"  Use TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}"
            )

        self.stdout.write(
            f"  From Email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}"
        )
        self.stdout.write("")

        # Send test email
        self.stdout.write(self.style.HTTP_INFO(f"📤 Sending test email to: {recipient}"))
        self.stdout.write("-" * 70)

        try:
            subject = "AREA - Email Configuration Test"
            message = f"""
Hello,

This is a test email from the AREA platform.

If you received this email, your email configuration is working correctly!

Technical details:
- Backend: {settings.EMAIL_BACKEND}
- From: {settings.DEFAULT_FROM_EMAIL}
- Recipient: {recipient}

Best regards,
The AREA Team
"""

            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">✅ Email Test Successful!</h1>
    </div>

    <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px;">Hello,</p>

        <p style="font-size: 16px;">This is a test email from the <strong>AREA platform</strong>.</p>

        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #22c55e;">
            <p style="margin: 0; color: #22c55e; font-weight: bold; font-size: 18px;">
                ✓ Your email configuration is working correctly!
            </p>
        </div>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

        <p style="font-size: 14px; color: #666;">
            <strong>Technical Details:</strong>
        </p>
        <ul style="font-size: 14px; color: #666;">
            <li>Backend: <code>{settings.EMAIL_BACKEND}</code></li>
            <li>From: <code>{settings.DEFAULT_FROM_EMAIL}</code></li>
            <li>Recipient: <code>{recipient}</code></li>
        </ul>

        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            Best regards,<br>
            <strong>The AREA Team</strong>
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; padding: 20px; color: #999; font-size: 12px;">
        <p>This is an automated test email from AREA platform.</p>
    </div>
</body>
</html>
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("✅ Test email sent successfully!"))
            self.stdout.write("")
            self.stdout.write(
                "Please check your inbox (and spam folder) for the test email."
            )
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 70))

        except Exception as e:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR(f"❌ Error sending test email: {e}"))
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Possible issues:"))
            self.stdout.write("  1. Check SMTP credentials in .env file")
            self.stdout.write(
                "  2. Verify EMAIL_HOST_PASSWORD is correct (use Gmail App Password)"
            )
            self.stdout.write("  3. Check firewall/network settings")
            self.stdout.write("  4. Verify SMTP server is reachable")
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("=" * 70))
            raise CommandError(f"Failed to send test email: {e}")
