"""Views for password reset functionality."""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

            # Build reset URL
            frontend_url = request.build_absolute_uri("/").rstrip("/")
            reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"

            # Send email
            subject = "Password Reset Request - AREA"
            html_message = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.username},</p>
                <p>You have requested to reset your password for your AREA account.</p>
                <p>Click the link below to reset your password:</p>
                <p>
                    <a href="{reset_url}"
                    style="background-color: #4CAF50; color: white;
                    padding: 10px 20px; text-decoration: none;
                    border-radius: 5px; display: inline-block;">
                    Reset Password</a>
                </p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{reset_url}</p>
                <p>This link will expire in 1 hour.</p>
                <p>
                    If you did not request a password reset,
                    please ignore this email.
                </p>
                <br>
                <p>Best regards,<br>The AREA Team</p>
            </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email="epi.areaction@gmail.com",
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

        logger.info(f"Password reset successful for user: {user.username}")

        return Response(
            {"message": "Password has been reset successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticated]

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

        logger.info(f"Password changed successfully for user: {user.username}")

        return Response(
            {"message": "Password has been changed successfully."},
            status=status.HTTP_200_OK,
        )
