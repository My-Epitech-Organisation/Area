##
## EPITECH PROJECT, 2025
## Area
## File description:
## views
##

import secrets
import string
import logging
from datetime import timedelta

from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.http import urlencode

from .models import OAuthNotification, User
from .serializers import (
    EmailTokenObtainPairSerializer,
    OAuthNotificationSerializer,
    UserProfileSerializer,
    UserSerializer,
)


logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    Creates a new user account and automatically sends an email verification link.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """Save user and send verification email."""
        user = serializer.save()

        # Generate verification token with 24h expiration
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save()

        # Send verification email
        try:
            logger.info(f"Sending verification email to {user.email}")
            self._send_verification_email(user, token)
            logger.info(f"Verification email sent successfully to {user.email}")
        except Exception as e:
            # Log error but don't fail registration
            logger.error(f"Failed to send verification email to {user.email}: {e}", exc_info=True)
            print(f"Warning: Failed to send verification email: {e}")

    def _send_verification_email(self, user, token):
        """Send email verification link to user."""
        subject = "AREA - Verify Your Email Address"

        # Build verification URL
        verification_url = self.request.build_absolute_uri(
            f"/auth/verify-email/{token}/"
        )

        # Plain text message
        message = f"""
Hello {user.username or user.email.split('@')[0]},

Welcome to AREA! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The AREA Team
"""

        # HTML message
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to AREA!</h1>
    </div>

    <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px;">Hello <strong>{user.username or user.email.split('@')[0]}</strong>,</p>

        <p style="font-size: 16px;">Thank you for creating an account with AREA! We're excited to have you on board.</p>

        <p style="font-size: 16px;">Please verify your email address by clicking the button below:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white;
                      padding: 15px 40px;
                      text-decoration: none;
                      border-radius: 5px;
                      font-weight: bold;
                      display: inline-block;
                      font-size: 16px;">
                Verify Email Address
            </a>
        </div>

        <p style="font-size: 14px; color: #666;">Or copy and paste this link into your browser:</p>
        <p style="font-size: 12px; color: #667eea; word-break: break-all; background-color: #fff; padding: 10px; border-radius: 5px;">
            {verification_url}
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

        <p style="font-size: 14px; color: #666;">
            <strong>Note:</strong> This link will expire in 24 hours for security reasons.
        </p>

        <p style="font-size: 14px; color: #666;">
            If you didn't create an account with AREA, please ignore this email.
        </p>

        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            Best regards,<br>
            <strong>The AREA Team</strong>
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; padding: 20px; color: #999; font-size: 12px;">
        <p>This is an automated email. Please do not reply to this message.</p>
    </div>
</body>
</html>
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user

        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendEmailVerificationView(APIView):
    """
    Resend email verification link to authenticated user.

    Allows users to request a new verification email if they didn't receive
    the original one or if the token expired.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        if user.email_verified:
            return Response(
                {"message": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new verification token with 24h expiration
        token = secrets.token_urlsafe(32)
        user.email_verification_token = token
        user.email_verification_token_expires = timezone.now() + timedelta(hours=24)
        user.save()

        # Send verification email
        try:
            self._send_verification_email(user, token, request)

            return Response(
                {
                    "message": "Verification email sent successfully",
                    "email": user.email,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _send_verification_email(self, user, token, request):
        """Send email verification link to user."""
        subject = "AREA - Verify Your Email Address"

        # Build verification URL
        verification_url = request.build_absolute_uri(
            f"/auth/verify-email/{token}/"
        )

        # Plain text message
        message = f"""
Hello {user.username or user.email.split('@')[0]},

You requested to verify your email address for your AREA account.

Please click the link below to verify your email:

{verification_url}

This link will expire in 24 hours.

If you didn't request this verification, please ignore this email.

Best regards,
The AREA Team
"""

        # HTML message
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">Verify Your Email</h1>
    </div>

    <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px;">Hello <strong>{user.username or user.email.split('@')[0]}</strong>,</p>

        <p style="font-size: 16px;">You requested to verify your email address for your AREA account.</p>

        <p style="font-size: 16px;">Please click the button below to complete the verification:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white;
                      padding: 15px 40px;
                      text-decoration: none;
                      border-radius: 5px;
                      font-weight: bold;
                      display: inline-block;
                      font-size: 16px;">
                Verify Email Address
            </a>
        </div>

        <p style="font-size: 14px; color: #666;">Or copy and paste this link into your browser:</p>
        <p style="font-size: 12px; color: #667eea; word-break: break-all; background-color: #fff; padding: 10px; border-radius: 5px;">
            {verification_url}
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

        <p style="font-size: 14px; color: #666;">
            <strong>Note:</strong> This link will expire in 24 hours for security reasons.
        </p>

        <p style="font-size: 14px; color: #666;">
            If you didn't request this verification, please ignore this email.
        </p>

        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            Best regards,<br>
            <strong>The AREA Team</strong>
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; padding: 20px; color: #999; font-size: 12px;">
        <p>This is an automated email. Please do not reply to this message.</p>
    </div>
</body>
</html>
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class VerifyEmailView(APIView):
    """
    Email verification endpoint.

    Verifies a user's email address using the token sent via email.
    Can be accessed without authentication (public endpoint).
    Redirects to frontend with verification result.
    """
    permission_classes = (AllowAny,)

    def get(self, request, token):
        # Get frontend URL from settings or environment
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

        try:
            user = User.objects.get(email_verification_token=token)

            if user.email_verified:
                # Already verified - redirect to login with info message
                params = urlencode({
                    'verified': 'true',
                    'already_verified': 'true',
                    'message': 'Your email is already verified. You can log in.',
                })
                return redirect(f"{frontend_url}/login?{params}")

            # Check if token is expired
            if not user.is_email_verification_token_valid():
                # Expired token - redirect to resend page
                params = urlencode({
                    'verified': 'false',
                    'expired': 'true',
                    'error': 'Verification token has expired. Please request a new one.',
                })
                return redirect(f"{frontend_url}/login?{params}")

            # Mark email as verified
            user.email_verified = True
            user.email_verification_token = ""  # Clear the token
            user.email_verification_token_expires = None
            user.save()

            # Success - redirect to login with success message
            params = urlencode({
                'verified': 'true',
                'message': 'Email verified successfully! You can now log in.',
                'email': user.email,
            })
            return redirect(f"{frontend_url}/login?{params}")

        except User.DoesNotExist:
            # Invalid token - redirect to login with error
            params = urlencode({
                'verified': 'false',
                'error': 'Invalid verification link. Please try again or request a new one.',
            })
            return redirect(f"{frontend_url}/login?{params}")


class EmailTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT token pair using email as credential."""

    serializer_class = EmailTokenObtainPairSerializer


class OAuthNotificationListView(generics.ListAPIView):
    serializer_class = OAuthNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OAuthNotification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
