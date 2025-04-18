from rest_framework.throttling import SimpleRateThrottle
from rest_framework.exceptions import Throttled
from users.utils import get_client_ip

class OTPAttemptThrottle(SimpleRateThrottle):
    scope = "otp_attempts"

    def get_cache_key(self, request, view):
        phone_number = request.data.get("phone_number")
        if phone_number:
            return f"otp_throttle:{phone_number}"
        return None 

    def throttle_failure(self):
        raise Throttled(detail="شما بیش از حد مجاز درخواست ارسال کرده‌اید. لطفاً بعد از {} ثانیه دوباره تلاش کنید.".format(int(self.wait())))



class LoginAttemptThrottle(SimpleRateThrottle):
    scope = "login_attempts"

    def get_cache_key(self, request, view):
        ip = get_client_ip(request)
        return f"login_throttle:{ip}"
    
    def throttle_failure(self):
        raise Throttled(detail="شما بیش از حد مجاز درخواست ارسال کرده‌اید. لطفاً بعد از {} ثانیه دوباره تلاش کنید.".format(int(self.wait())))
