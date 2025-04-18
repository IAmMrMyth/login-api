from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection
from rest_framework_simplejwt.tokens import RefreshToken

from users.utils import generate_otp
from users.api.serializers import (
    PhoneNumberSerializer,
    OTPVerificationSerializer,
)
from users.models import CustomUser


class LoginRequestView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        response_data = {}
        if not user:
            response_data["is_new_user"] = True
            response_data["otp_sent"] = True
        else:
            response_data["is_new_user"] = False
            response_data["otp_sent"] = False

        otp = generate_otp()
        redis_connection = get_redis_connection("default")
        redis_connection.setex(f"otp_{phone_number}", 60 * 5, otp)
        return Response(response_data, status=status.HTTP_200_OK)


class OTPVerificationView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]
        redis_connection = get_redis_connection("default")
        stored_otp = redis_connection.get(f"otp_{phone_number}")
        if not stored_otp:
            return Response(
                {"error": "کد تایید منقضی شده یا وجود ندارد"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if stored_otp.decode() != otp:
            return Response(
                {"error": "کد تایید اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
            )
        user, created = CustomUser.objects.get_or_create(phone_number=phone_number)
        refresh = RefreshToken.for_user(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_verified": user.is_verified,
        }
        redis_connection.delete(f"otp_{phone_number}")
        return Response(data, status=status.HTTP_200_OK)


class LoginWithPasswordView(generics.GenericAPIView):
    serializer_class = LoginWithPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "کاربری با این شماره تلفن یافت نشد"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.check_password(password):
            return Response(
                {"error": "رمز عبور اشتباه است"}, status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_verified": user.is_verified,
        }
        return Response(data, status=status.HTTP_200_OK)
