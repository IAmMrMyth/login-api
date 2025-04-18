from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField("ایمیل",unique=True)
    phone_number = models.CharField("شماره تلفن",max_length=10, unique=True)
    first_name = models.CharField("نام",max_length=100)
    last_name = models.CharField("نام خانوادگی",max_length=100)
    is_verified = models.BooleanField("تایید شده",default=False)
    
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.username