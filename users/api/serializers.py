from rest_framework import serializers
from users.models import CustomUser


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label="شماره تلفن", max_length=10)


class OTPVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label="شماره تلفن", max_length=10)
    otp = serializers.CharField(label="کد تایید", max_length=6)


class LoginWithPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label="شماره تلفن", max_length=10)
    password = serializers.CharField(label="رمز عبور", max_length=128)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "phone_number", "email", "first_name", "last_name"]
        read_only_fields = ["id", "phone_number"]
