from django.urls import path
from users.api.views import (
    LoginRequestView,
    OTPVerificationView,
    LoginWithPasswordView,
    ProfileUpdateView,
)

app_name = 'users'
urlpatterns = [
    path('login/', LoginRequestView.as_view(), name='login'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp-verification'),
    path('login-with-password/', LoginWithPasswordView.as_view(), name='login-with-password'),
    path('profile-update/', ProfileUpdateView.as_view(), name='profile-update'),
]