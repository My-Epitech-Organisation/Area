##
## EPITECH PROJECT, 2025
## Area
## File description:
## views
##

import secrets
import string

from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings
from django.core.mail import send_mail

from .models import OAuthNotification, User
from .serializers import (
    EmailTokenObtainPairSerializer,
    OAuthNotificationSerializer,
    UserProfileSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        if user.email_verified:
            return Response(
                {"message": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate verification token
        token = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
        user.email_verification_token = token
        user.save()

        # Send email (stub - just mark as verified for now)
        # In production, you would send a real email with the verification link
        try:
            subject = "AREA - Email Verification"
            message = f"""
            Hello,

            Please click the following link to verify your email address:
            {request.build_absolute_uri(f"/auth/verify-email/{token}/")}

            If you didn't request this verification, please ignore this email.

            Best regards,
            AREA Team
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {"message": "Verification email sent successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, token):
        try:
            user = User.objects.get(email_verification_token=token)

            if user.email_verified:
                return Response(
                    {"message": "Email is already verified"}, status=status.HTTP_200_OK
                )

            # Mark email as verified
            user.email_verified = True
            user.email_verification_token = ""  # Clear the token
            user.save()

            return Response(
                {"message": "Email verified successfully"}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
