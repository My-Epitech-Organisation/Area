from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path

from .oauth_views import (
    OAuthCallbackView,
    OAuthInitiateView,
    ServiceConnectionListView,
    ServiceDisconnectView,
)
from .password_views import (
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)
from .views import (
    EmailOrUsernameTokenObtainPairView,
    RegisterView,
    SendEmailVerificationView,
    UserDetailView,
    VerifyEmailView,
)

urlpatterns = [
    # Authentication endpoints
    path("register/", RegisterView.as_view(), name="auth_register"),
    path(
        "login/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserDetailView.as_view(), name="user_detail"),
    path(
        "send-verification-email/",
        SendEmailVerificationView.as_view(),
        name="send_verification_email",
    ),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    # Password management endpoints
    path(
        "password-reset/",
        ForgotPasswordView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        ResetPasswordView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/change/",
        ChangePasswordView.as_view(),
        name="password_change",
    ),
    # OAuth2 endpoints
    path(
        "oauth/<str:provider>/",
        OAuthInitiateView.as_view(),
        name="oauth_initiate",
    ),
    path(
        "oauth/<str:provider>/callback/",
        OAuthCallbackView.as_view(),
        name="oauth_callback",
    ),
    path(
        "services/",
        ServiceConnectionListView.as_view(),
        name="services_list",
    ),
    path(
        "services/<str:provider>/disconnect/",
        ServiceDisconnectView.as_view(),
        name="service_disconnect",
    ),
]
