from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره تلفن الزامی است")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField("ایمیل", unique=True)
    phone_number = models.CharField("شماره تلفن", max_length=10, unique=True)
    first_name = models.CharField("نام", max_length=100)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    is_verified = models.BooleanField("تایید شده", default=False)
    username = None
    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.username
