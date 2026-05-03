from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PasswordResetToken
from .serializers import ForgotPasswordSerializer, LoginSerializer, ResetPasswordSerializer

User = get_user_model()


def ensure_demo_users():
    if User.objects.exists():
        return

    User.objects.create_user(
        username="manager",
        email="manager@rvms.com",
        password="manager123",
        first_name="Runway",
        last_name="Manager",
        is_staff=True,
    )
    User.objects.create_user(
        username="officer",
        email="officer@rvms.com",
        password="officer123",
        first_name="Safety",
        last_name="Officer",
        is_staff=True,
    )


def build_user_payload(user):
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
    return {
        "id": user.pk,
        "username": user.username,
        "name": full_name,
        "email": user.email,
        "role": "Manager" if user.is_superuser or user.username == "manager" else "Safety Officer",
        "airport": "RVMS Operations",
    }


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        ensure_demo_users()

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip()
        password = serializer.validated_data["password"]

        user = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()
        if not user or not check_password(password, user.password):
            return Response({"detail": "Invalid email/username or password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"detail": "This account is inactive."}, status=status.HTTP_403_FORBIDDEN)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response(
            {
                "token": f"session-{user.pk}-{int(timezone.now().timestamp())}",
                "user": build_user_payload(user),
                "demo_credentials": [
                    {"email": "manager@rvms.com", "password": "manager123"},
                    {"email": "officer@rvms.com", "password": "officer123"},
                ],
            }
        )


class ForgotPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        ensure_demo_users()

        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"detail": "No account was found for that email."}, status=status.HTTP_404_NOT_FOUND)

        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=30),
        )

        return Response(
            {
                "message": "Reset token generated successfully.",
                "token": reset_token.token,
                "email": user.email,
                "expires_at": reset_token.expires_at.isoformat(),
            }
        )


class ResetPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_value = serializer.validated_data["token"].strip()
        reset_token = PasswordResetToken.objects.filter(token=token_value).select_related("user").first()
        if not reset_token:
            return Response({"detail": "Reset token is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        if reset_token.used_at is not None:
            return Response({"detail": "Reset token has already been used."}, status=status.HTTP_400_BAD_REQUEST)
        if reset_token.expires_at <= timezone.now():
            return Response({"detail": "Reset token has expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        reset_token.mark_used()

        return Response({"message": "Password updated successfully."})
