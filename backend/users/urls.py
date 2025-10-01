from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from .views import (
    RegisterView,
    SendEmailVerificationView,
    UserDetailView,
    VerifyEmailView,
    EmailOrUsernameTokenObtainPairView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserDetailView.as_view(), name="user_detail"),
    path(
        "send-verification-email/",
        SendEmailVerificationView.as_view(),
        name="send_verification_email",
    ),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
]
