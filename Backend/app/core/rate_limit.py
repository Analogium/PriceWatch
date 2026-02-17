"""
Rate limiting middleware using Redis.
"""

import time
from typing import Optional

from fastapi import HTTPException, Request, status
from redis import Redis

from app.core.config import settings
from app.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, t


class RateLimiter:
    def __init__(self, redis_client: Optional[Redis] = None):
        """Initialize rate limiter with Redis client."""
        self.redis_client = redis_client
        self.requests = settings.RATE_LIMIT_REQUESTS
        self.period = settings.RATE_LIMIT_PERIOD

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host if request.client else "unknown"

    def is_rate_limited(self, key: str) -> bool:
        """
        Check if the key has exceeded the rate limit.
        Returns True if rate limited, False otherwise.
        """
        if not self.redis_client:
            # If Redis is not available, don't rate limit
            return False

        try:
            current_time = int(time.time())
            window_key = f"rate_limit:{key}:{current_time // self.period}"

            # Increment the counter
            count: int = self.redis_client.incr(window_key)  # type: ignore[assignment]

            # Set expiration on first request
            if count == 1:
                self.redis_client.expire(window_key, self.period * 2)

            return count > self.requests

        except Exception as e:
            # If Redis fails, don't block the request
            print(f"Rate limiter error: {e}")
            return False

    async def check_rate_limit(self, request: Request):
        """
        Middleware function to check rate limit.
        Raises HTTPException if rate limited.
        """
        client_ip = self.get_client_ip(request)

        if self.is_rate_limited(client_ip):
            # Parse Accept-Language for rate limit messages
            accept_lang = request.headers.get("Accept-Language") or ""
            primary = accept_lang.split(",")[0].split(";")[0].strip().split("-")[0].lower()
            lang = primary if primary in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=t("rate_limit_exceeded", lang, requests=self.requests, period=self.period),
            )


# Create rate limiter instance
try:
    from redis import Redis

    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    rate_limiter = RateLimiter(redis_client)
except Exception as e:
    print(f"Redis connection failed for rate limiter: {e}")
    rate_limiter = RateLimiter(None)
