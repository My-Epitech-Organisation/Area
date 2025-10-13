##
## EPITECH PROJECT, 2025
## Area
## File description:
## google_signin
##

"""Google Sign-In authentication views for mobile."""

import logging

from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

from ..serializers import GoogleLoginSerializer
from .manager import OAuthManager

logger = logging.getLogger(__name__)


class GoogleLoginView(GenericAPIView):
    """
    Handle Google Sign-In authentication for mobile apps.

    POST /auth/google-login/

    Accepts a Google ID token from the mobile app and authenticates the user.
    If the user doesn't exist, creates a new account.

    Request body:
        {
            "id_token": "google_id_token_here"
        }

    Returns:
        {
            "access": "jwt_access_token",
            "refresh": "jwt_refresh_token",
            "user": {
                "id": 1,
                "username": "user@example.com",
                "email": "user@example.com"
            }
        }
    """

    permission_classes = [AllowAny]
    serializer_class = GoogleLoginSerializer

    def post(self, request):
        """Authenticate user with Google ID token."""
        id_token_str = request.data.get("id_token")

        if not id_token_str:
            return Response(
                {"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify the ID token
            google_client_id = getattr(settings, "GOOGLE_CLIENT_ID", None)

            if not google_client_id:
                logger.error("GOOGLE_CLIENT_ID not configured in settings")
                return Response(
                    {"error": "Google authentication not configured"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), google_client_id
            )

            # Verify issuer
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer")

            # Get user info from token
            email = idinfo.get("email")
            google_id = idinfo.get("sub")
            name = idinfo.get("name", "")
            email_verified = idinfo.get("email_verified", False)
            picture = idinfo.get("picture", "")

            if not email:
                return Response(
                    {"error": "Email not provided by Google"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use the centralized method to get or create user
            user, created = OAuthManager.get_or_create_google_user(
                email=email,
                google_id=google_id,
                name=name,
                email_verified=email_verified,
                picture=picture,
            )

            action = "created" if created else "logged in"
            logger.info(f"User {action} via Google Sign-In: {email}")

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "message": "Successfully authenticated with Google",
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            logger.error(f"Invalid Google ID token: {str(e)}")
            return Response(
                {"error": "Invalid ID token"}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Google Sign-In error: {str(e)}", exc_info=True)
            return Response(
                {"error": "Authentication failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
