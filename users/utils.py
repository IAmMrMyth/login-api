import ipaddress
from django_redis import get_redis_connection
import random

def generate_otp():
    return random.randint(100000, 999999)


def get_client_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    return ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')

def check_blocked(key_prefix, identifier):
    redis = get_redis_connection("default")
    key = f"{key_prefix}:{identifier}"
    return redis.exists(key)

def add_block(key_prefix, identifier, ttl=3600):
    redis = get_redis_connection("default")
    key = f"{key_prefix}:{identifier}"
    redis.setex(key, ttl, "blocked")