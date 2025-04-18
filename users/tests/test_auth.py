from rest_framework.test import APITestCase
from django.urls import reverse
from django_redis import get_redis_connection
from users.models import CustomUser
from users.utils import generate_otp
from django.core.cache import cache
from time import sleep


class PhoneNumberLoginTestCase(APITestCase):
    def setUp(self):
        redis = get_redis_connection("default")
        redis.flushall()

    def test_send_otp_to_new_user(self):
        url = reverse("users:login")
        data = {"phone_number": "9399857569"}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        redis = get_redis_connection("default")
        self.assertTrue(redis.exists("otp_9399857569"))

    def test_existing_user_not_send_otp(self):
        user = CustomUser.objects.create_user(phone_number="9399857569")
        url = reverse("users:login")
        data = {"phone_number": "9399857569"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["otp_sent"], False)
        redis = get_redis_connection("default")
        self.assertFalse(redis.exists("otp_9399857569"))

    def test_invalid_phone_number(self):
        url = reverse("users:login")
        data = {"phone_number": "09213456789"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["phone_number"][0],
            "مطمعن شوید طول این مقدار بیشتر از 10 نیست.",
        )


class OTPVerificationTestCase(APITestCase):
    def setUp(self):
        redis = get_redis_connection("default")
        redis.flushall()

        self.user = CustomUser.objects.create_user(phone_number="9399857569")
        self.otp = generate_otp()
        redis = get_redis_connection("default")
        redis.set(f"otp_{self.user.phone_number}", self.otp)

    def test_valid_otp(self):
        url = reverse("users:otp-verification")
        data = {"phone_number": self.user.phone_number, "otp": self.otp}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get("access", None), None)
        self.assertNotEqual(response.data.get("refresh", None), None)

    def test_invalid_otp(self):
        url = reverse("users:otp-verification")
        data = {"phone_number": self.user.phone_number, "otp": "123456"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("error"), "کد تایید اشتباه است")

    def test_not_stored_otp(self):
        url = reverse("users:otp-verification")
        data = {"phone_number": "1234567890", "otp": "123456"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("error"), "کد تایید منقضی شده یا وجود ندارد")

    def test_rate_limit(self):
        url = reverse("users:otp-verification")
        data = {"phone_number": "1234567890", "otp": "123456"}
        for _ in range(3):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 429)

class TestLoginWithPassword(APITestCase):
    def setUp(self):
        redis = get_redis_connection("default")
        redis.flushall()
        self.user = CustomUser.objects.create_user(phone_number="9399857569")
        self.user.set_password("password")
        self.user.save()

    def test_valid_password(self):
        url = reverse("users:login-with-password")
        data = {"phone_number": self.user.phone_number, "password": "password"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get("access", None), None)
        self.assertNotEqual(response.data.get("refresh", None), None)

    def test_invalid_password(self):
        url = reverse("users:login-with-password")
        data = {"phone_number": self.user.phone_number, "password": "wrong_password"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("error"), "نام کاربری یا رمز عبور اشتباه است")

    def test_rate_limit(self):
        url = reverse("users:login-with-password")
        data = {"phone_number": self.user.phone_number, "password": "wrong_password"}
        for _ in range(3):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 429)
