from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection
from rest_framework_simplejwt.tokens import RefreshToken

from users.throttles import OTPAttemptThrottle, LoginAttemptThrottle
from users.utils import generate_otp
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.api.serializers import (
    PhoneNumberSerializer,
    OTPVerificationSerializer,
    LoginWithPasswordSerializer,
    ProfileSerializer,
)
from users.models import CustomUser
from django_kavenegar.common import send_otp


class LoginRequestView(generics.GenericAPIView):
    serializer_class = PhoneNumberSerializer
    throttle_classes = [LoginAttemptThrottle]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        response_data = {}
        if not user:
            response_data["is_new_user"] = True
            response_data["otp_sent"] = True
            otp = generate_otp()
            send_otp(phone_number, otp)
            print(otp)
            redis_connection = get_redis_connection("default")
            redis_connection.setex(f"otp_{phone_number}", 60 * 5, otp)
        else:
            response_data["is_new_user"] = False
            response_data["otp_sent"] = False

        return Response(response_data, status=status.HTTP_200_OK)


class OTPVerificationView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer
    throttle_classes = [OTPAttemptThrottle]

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
    throttle_classes = [LoginAttemptThrottle]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:

            return Response(
                {"error": "نام کاربری یا رمز عبور اشتباه است"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.check_password(password):

            return Response(
                {"error": "نام کاربری یا رمز عبور اشتباه است"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = RefreshToken.for_user(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_verified": user.is_verified,
        }
        return Response(data, status=status.HTTP_200_OK)


class ProfileUpdateView(generics.GenericAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.first_name = serializer.validated_data["first_name"]
        user.last_name = serializer.validated_data["last_name"]
        user.email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user.is_verified = True
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
