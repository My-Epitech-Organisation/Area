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

from .models import User
from .serializers import EmailTokenObtainPairSerializer, UserSerializer, ItemSerializer

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

@extend_schema_view(
    list=extend_schema(
        summary="List Items",
        description="Retrieve a list of items.",
        responses=ItemSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve Item",
        description="Retrieve a specific item by ID.",
        responses=ItemSerializer(),
    ),
)

@extend_schema(
    tags=["Items"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Item ID",
        )
    ]
)
class ItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For schema generation, return empty queryset
        if getattr(self, "swagger_fake_view", False):
            return []
        return []  # This is a simple example ViewSet

    def list(self, request):
        data = [
            {"id": 1, "name": "Item 1", "price": "9.99"}
        ]
        return Response(data)
    def retrieve(self, request, pk=None):
        item = {"id": int(pk), "name": f"Item {pk}", "price": "9.99"}
        return Response(item)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SendEmailVerificationView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = None  # No serializer needed for this endpoint

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
    serializer_class = None  # No serializer needed for this endpoint

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
