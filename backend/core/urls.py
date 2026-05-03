from django.urls import path

from .views import ForgotPasswordAPIView, LoginAPIView, ResetPasswordAPIView


urlpatterns = [
    path("api/auth/login/", LoginAPIView.as_view(), name="api_auth_login"),
    path("api/auth/forgot-password/", ForgotPasswordAPIView.as_view(), name="api_auth_forgot_password"),
    path("api/auth/reset-password/", ResetPasswordAPIView.as_view(), name="api_auth_reset_password"),
]
