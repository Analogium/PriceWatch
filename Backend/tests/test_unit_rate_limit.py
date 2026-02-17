"""
Unit tests for rate limiting functionality.
Tests Redis-based rate limiting with mocked Redis client.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from redis import Redis

from app.core.rate_limit import RateLimiter


@pytest.mark.unit
class TestRateLimiter:
    """Test suite for RateLimiter class."""

    def test_rate_limiter_initialization_with_redis(self):
        """Test RateLimiter initialization with Redis client."""
        mock_redis = Mock(spec=Redis)
        rate_limiter = RateLimiter(redis_client=mock_redis)

        assert rate_limiter.redis_client == mock_redis
        assert rate_limiter.requests > 0
        assert rate_limiter.period > 0

    def test_rate_limiter_initialization_without_redis(self):
        """Test RateLimiter initialization without Redis client."""
        rate_limiter = RateLimiter(redis_client=None)

        assert rate_limiter.redis_client is None
        assert rate_limiter.requests > 0
        assert rate_limiter.period > 0

    def test_get_client_ip_from_x_forwarded_for(self):
        """Test extracting IP from X-Forwarded-For header."""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "192.168.1.1, 10.0.0.1"
        mock_request.client = None

        rate_limiter = RateLimiter()
        ip = rate_limiter.get_client_ip(mock_request)

        assert ip == "192.168.1.1"
        mock_request.headers.get.assert_called_once_with("X-Forwarded-For")

    def test_get_client_ip_from_request_client(self):
        """Test extracting IP from request.client when no X-Forwarded-For."""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None
        mock_client = Mock()
        mock_client.host = "127.0.0.1"
        mock_request.client = mock_client

        rate_limiter = RateLimiter()
        ip = rate_limiter.get_client_ip(mock_request)

        assert ip == "127.0.0.1"

    def test_get_client_ip_no_client(self):
        """Test IP extraction when request.client is None."""
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None
        mock_request.client = None

        rate_limiter = RateLimiter()
        ip = rate_limiter.get_client_ip(mock_request)

        assert ip == "unknown"

    def test_is_rate_limited_no_redis(self):
        """Test that rate limiting is disabled when Redis is unavailable."""
        rate_limiter = RateLimiter(redis_client=None)

        result = rate_limiter.is_rate_limited("test_key")

        assert result is False

    def test_is_rate_limited_below_limit(self):
        """Test when request count is below the rate limit."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 1  # First request

        rate_limiter = RateLimiter(redis_client=mock_redis)
        rate_limiter.requests = 100  # Set high limit

        result = rate_limiter.is_rate_limited("192.168.1.1")

        assert result is False
        assert mock_redis.incr.called
        assert mock_redis.expire.called

    def test_is_rate_limited_exceeds_limit(self):
        """Test when request count exceeds the rate limit."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 101  # Exceeds limit

        rate_limiter = RateLimiter(redis_client=mock_redis)
        rate_limiter.requests = 100

        result = rate_limiter.is_rate_limited("192.168.1.1")

        assert result is True

    def test_is_rate_limited_sets_expiration_on_first_request(self):
        """Test that expiration is set only on the first request."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 1  # First request

        rate_limiter = RateLimiter(redis_client=mock_redis)
        rate_limiter.period = 60

        rate_limiter.is_rate_limited("192.168.1.1")

        mock_redis.expire.assert_called_once()
        # Expiration should be 2x the period
        assert mock_redis.expire.call_args[0][1] == 120

    def test_is_rate_limited_no_expiration_on_subsequent_requests(self):
        """Test that expiration is not set on subsequent requests."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 5  # Not first request

        rate_limiter = RateLimiter(redis_client=mock_redis)

        rate_limiter.is_rate_limited("192.168.1.1")

        mock_redis.expire.assert_not_called()

    def test_is_rate_limited_redis_error(self):
        """Test that Redis errors don't block requests."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.side_effect = Exception("Redis connection failed")

        rate_limiter = RateLimiter(redis_client=mock_redis)

        result = rate_limiter.is_rate_limited("192.168.1.1")

        assert result is False  # Should not block on error

    @pytest.mark.asyncio
    async def test_check_rate_limit_not_limited(self):
        """Test middleware when request is not rate limited."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 1

        rate_limiter = RateLimiter(redis_client=mock_redis)

        mock_request = Mock(spec=Request)

        def headers_get(key, default=None):
            headers = {"Accept-Language": "en"}
            return headers.get(key, default)

        mock_request.headers.get = headers_get
        mock_client = Mock()
        mock_client.host = "192.168.1.1"
        mock_request.client = mock_client

        # Should not raise exception
        await rate_limiter.check_rate_limit(mock_request)

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeds_limit(self):
        """Test middleware when request exceeds rate limit."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 101

        rate_limiter = RateLimiter(redis_client=mock_redis)
        rate_limiter.requests = 100
        rate_limiter.period = 60

        mock_request = Mock(spec=Request)

        def headers_get(key, default=None):
            headers = {"Accept-Language": "en"}
            return headers.get(key, default)

        mock_request.headers.get = headers_get
        mock_client = Mock()
        mock_client.host = "192.168.1.1"
        mock_request.client = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await rate_limiter.check_rate_limit(mock_request)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    def test_rate_limit_key_includes_time_window(self):
        """Test that rate limit key includes time window for sliding window."""
        mock_redis = Mock(spec=Redis)
        mock_redis.incr.return_value = 1

        rate_limiter = RateLimiter(redis_client=mock_redis)
        rate_limiter.period = 60

        with patch("app.core.rate_limit.time.time") as mock_time:
            mock_time.return_value = 1234567890

            rate_limiter.is_rate_limited("192.168.1.1")

            # Verify the key format includes time window
            call_args = mock_redis.incr.call_args[0][0]
            assert "rate_limit:192.168.1.1:" in call_args
            assert str(1234567890 // 60) in call_args

    def test_multiple_ips_tracked_separately(self):
        """Test that different IPs have separate rate limit counters."""
        mock_redis = Mock(spec=Redis)

        rate_limiter = RateLimiter(redis_client=mock_redis)

        # Simulate different IPs
        mock_redis.incr.return_value = 1
        rate_limiter.is_rate_limited("192.168.1.1")

        mock_redis.incr.return_value = 1
        rate_limiter.is_rate_limited("192.168.1.2")

        # Should be called twice with different keys
        assert mock_redis.incr.call_count == 2
        call_keys = [call[0][0] for call in mock_redis.incr.call_args_list]
        assert "192.168.1.1" in call_keys[0]
        assert "192.168.1.2" in call_keys[1]
