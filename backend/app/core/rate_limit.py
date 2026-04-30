from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Global rate limiter using the client's IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
