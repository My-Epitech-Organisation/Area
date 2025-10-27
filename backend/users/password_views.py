##
## EPITECH PROJECT, 2025
## Area
## File description:
## password_views
##

"""Views for password reset functionality."""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.html import strip_tags

from .models import PasswordResetToken
from .password_serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ForgotPasswordView(APIView):
    """Request a password reset email."""

    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        """Send password reset email if user exists."""
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # Always return success to prevent user enumeration
        try:
            user = User.objects.get(email=email)

            # Invalidate any existing unused tokens for this user
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

            # Create new reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Build reset URL using frontend URL
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"

            # Send email
            subject = "Password Reset Request - AREA"
            html_message = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Request</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 12px; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">🔒 Password Reset</h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px; background-color: #fafbff;">
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                Hello,
                            </p>
                            <p style="margin: 0 0 20px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                You have requested to reset your password for your <strong style="color: #667eea;">AREA</strong> account.
                            </p>
                            <p style="margin: 0 0 30px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                Click the button below to create a new password:
                            </p>
                            <!-- Button -->
                            <table role="presentation" style="margin: 0 auto;">
                                <tr>
                                    <td style="border-radius: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
                                        <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; letter-spacing: 0.5px;">
                                            Reset My Password
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 30px 0 20px 0; color: #888888; font-size: 14px; line-height: 1.5; text-align: center;">
                                Or copy and paste this URL into your browser:
                            </p>
                            <p style="margin: 0 0 30px 0; padding: 15px; background-color: #f0f3ff; border-left: 4px solid #667eea; border-radius: 4px; word-break: break-all; color: #667eea; font-size: 13px; font-family: 'Courier New', monospace;">
                                {reset_url}
                            </p>
                            <div style="margin: 30px 0; padding: 20px; background-color: #fff8e6; border-left: 4px solid #ffc107; border-radius: 4px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                                    ⚠️ <strong>Security Notice:</strong> This link will expire in <strong>1 hour</strong>.
                                </p>
                            </div>
                            <p style="margin: 0; color: #999999; font-size: 14px; line-height: 1.5; text-align: center;">
                                If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background: linear-gradient(135deg, #f5f7ff 0%, #faf5ff 100%); border-radius: 0 0 12px 12px;">
                            <p style="margin: 0 0 10px 0; color: #667eea; font-size: 16px; font-weight: bold;">
                                The AREA Team
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                Automating your digital life, one action at a time
                            </p>
                        </td>
                    </tr>
                </table>
                <!-- Bottom text -->
                <table role="presentation" style="width: 600px; margin-top: 20px;">
                    <tr>
                        <td style="text-align: center;">
                            <p style="margin: 0; color: #ffffff; font-size: 12px; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                                This is an automated email. Please do not reply to this message.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password reset email sent to {email}")

        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            logger.warning(f"Password reset requested for non-existent email: {email}")

        # Always return success to prevent user enumeration
        return Response(
            {
                "message": (
                    "If an account exists with this email, "
                    "you will receive a password reset link shortly."
                )
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """Reset password using a token."""

    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        """Reset the user's password."""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]

        # Update user password
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Mark token as used
        reset_token.mark_used()

        logger.info(f"Password reset successful for user: {user.email}")

        return Response(
            {"message": "Password has been reset successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        """Change the user's password."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]

        # Update password
        user = request.user
        user.set_password(new_password)
        user.save()

        logger.info(f"Password changed successfully for user: {user.email}")

        return Response(
            {"message": "Password has been changed successfully."},
            status=status.HTTP_200_OK,
        )
