"""
Unit tests for advanced scraping features:
- User-Agent rotation
- Redis caching
- Circuit breaker
- Proxy rotation
"""

import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from redis import Redis

from app.services.scraper_advanced import CircuitBreaker, ProxyRotator, ScraperCache, UserAgentRotator


@pytest.mark.unit
class TestUserAgentRotator:
    """Test User-Agent rotation functionality."""

    def test_get_random_returns_valid_ua(self):
        """Test that get_random returns a valid User-Agent string."""
        ua = UserAgentRotator.get_random()
        assert ua is not None
        assert len(ua) > 50  # User-Agents are typically long
        assert "Mozilla" in ua  # Should contain Mozilla prefix

    def test_get_random_returns_different_uas(self):
        """Test that get_random returns different User-Agents over multiple calls."""
        uas = [UserAgentRotator.get_random() for _ in range(20)]
        # Should have multiple unique UAs (though not guaranteed every time)
        unique_uas = set(uas)
        assert len(unique_uas) > 1, "Should return different User-Agents"

    def test_get_headers_includes_user_agent(self):
        """Test that get_headers includes User-Agent header."""
        headers = UserAgentRotator.get_headers()
        assert "User-Agent" in headers
        assert len(headers["User-Agent"]) > 50

    def test_get_headers_full_includes_all_headers(self):
        """Test that get_headers with full=True includes all browser headers."""
        headers = UserAgentRotator.get_headers(include_full_headers=True)
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Accept-Language" in headers
        assert "Accept-Encoding" in headers
        assert "Connection" in headers
        assert len(headers) >= 8  # Should have many headers

    def test_get_headers_minimal_only_user_agent(self):
        """Test that get_headers with full=False only includes User-Agent."""
        headers = UserAgentRotator.get_headers(include_full_headers=False)
        assert "User-Agent" in headers
        assert len(headers) == 1  # Only User-Agent


@pytest.mark.unit
class TestScraperCache:
    """Test Redis-based scraping cache."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        redis_mock = Mock(spec=Redis)
        return redis_mock

    @pytest.fixture
    def cache(self, mock_redis):
        """Create cache instance with mocked Redis."""
        return ScraperCache(redis_client=mock_redis, default_ttl=3600)

    def test_init_with_default_ttl(self, cache):
        """Test cache initialization with default TTL."""
        assert cache.default_ttl == 3600
        assert cache.key_prefix == "scraper_cache:"

    def test_generate_cache_key_consistent(self, cache):
        """Test that cache key generation is consistent."""
        url = "https://www.amazon.fr/product/12345"
        key1 = cache._generate_cache_key(url)
        key2 = cache._generate_cache_key(url)
        assert key1 == key2
        assert key1.startswith("scraper_cache:")

    def test_generate_cache_key_different_for_different_urls(self, cache):
        """Test that different URLs generate different cache keys."""
        url1 = "https://www.amazon.fr/product/12345"
        url2 = "https://www.fnac.com/product/67890"
        key1 = cache._generate_cache_key(url1)
        key2 = cache._generate_cache_key(url2)
        assert key1 != key2

    def test_get_cache_hit(self, cache, mock_redis):
        """Test cache hit returns cached data."""
        url = "https://www.amazon.fr/product/12345"
        cached_data = {"name": "Test Product", "price": 99.99}
        mock_redis.get.return_value = json.dumps(cached_data)

        result = cache.get(url)
        assert result is not None
        assert result["name"] == "Test Product"
        assert result["price"] == 99.99
        mock_redis.get.assert_called_once()

    def test_get_cache_miss(self, cache, mock_redis):
        """Test cache miss returns None."""
        url = "https://www.amazon.fr/product/12345"
        mock_redis.get.return_value = None

        result = cache.get(url)
        assert result is None
        mock_redis.get.assert_called_once()

    def test_get_handles_redis_error(self, cache, mock_redis):
        """Test that get handles Redis errors gracefully."""
        url = "https://www.amazon.fr/product/12345"
        mock_redis.get.side_effect = Exception("Redis connection error")

        result = cache.get(url)
        assert result is None  # Should return None on error

    def test_set_caches_data(self, cache, mock_redis):
        """Test that set caches data successfully."""
        url = "https://www.amazon.fr/product/12345"
        data = {"name": "Test Product", "price": 99.99}

        result = cache.set(url, data)
        assert result is True
        mock_redis.setex.assert_called_once()

        # Check that cached data includes timestamp
        call_args = mock_redis.setex.call_args
        cached_value = json.loads(call_args[0][2])
        assert "cached_at" in cached_value
        assert cached_value["name"] == "Test Product"

    def test_set_uses_custom_ttl(self, cache, mock_redis):
        """Test that set uses custom TTL when provided."""
        url = "https://www.amazon.fr/product/12345"
        data = {"name": "Test Product"}
        custom_ttl = 1800

        cache.set(url, data, ttl=custom_ttl)

        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == custom_ttl

    def test_set_handles_redis_error(self, cache, mock_redis):
        """Test that set handles Redis errors gracefully."""
        url = "https://www.amazon.fr/product/12345"
        data = {"name": "Test Product"}
        mock_redis.setex.side_effect = Exception("Redis connection error")

        result = cache.set(url, data)
        assert result is False

    def test_invalidate_deletes_cache(self, cache, mock_redis):
        """Test that invalidate deletes cache entry."""
        url = "https://www.amazon.fr/product/12345"
        mock_redis.delete.return_value = 1

        result = cache.invalidate(url)
        assert result is True
        mock_redis.delete.assert_called_once()

    def test_invalidate_handles_missing_entry(self, cache, mock_redis):
        """Test that invalidate handles missing cache entry."""
        url = "https://www.amazon.fr/product/12345"
        mock_redis.delete.return_value = 0

        result = cache.invalidate(url)
        assert result is False

    def test_clear_all_deletes_all_entries(self, cache, mock_redis):
        """Test that clear_all deletes all scraper cache entries."""
        mock_redis.scan_iter.return_value = iter(["scraper_cache:key1", "scraper_cache:key2"])
        mock_redis.delete.return_value = 2

        count = cache.clear_all()
        assert count == 2
        mock_redis.scan_iter.assert_called_once_with(match="scraper_cache:*")


@pytest.mark.unit
class TestCircuitBreaker:
    """Test Circuit Breaker pattern."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        redis_mock = Mock(spec=Redis)
        redis_mock.get.return_value = None
        redis_mock.incr.return_value = 1
        return redis_mock

    @pytest.fixture
    def breaker(self, mock_redis):
        """Create circuit breaker with mocked Redis."""
        return CircuitBreaker(
            redis_client=mock_redis,
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=2,
        )

    def test_init_with_parameters(self, breaker):
        """Test circuit breaker initialization."""
        assert breaker.failure_threshold == 5
        assert breaker.recovery_timeout == 60
        assert breaker.success_threshold == 2

    def test_get_state_default_closed(self, breaker, mock_redis):
        """Test that default state is CLOSED."""
        mock_redis.get.return_value = None
        state = breaker.get_state("amazon")
        assert state == CircuitBreaker.STATE_CLOSED

    def test_get_state_returns_stored_state(self, breaker, mock_redis):
        """Test that get_state returns stored state from Redis."""
        mock_redis.get.return_value = CircuitBreaker.STATE_OPEN
        state = breaker.get_state("amazon")
        assert state == CircuitBreaker.STATE_OPEN

    def test_is_available_when_closed(self, breaker, mock_redis):
        """Test that requests are allowed when circuit is CLOSED."""
        mock_redis.get.return_value = CircuitBreaker.STATE_CLOSED
        assert breaker.is_available("amazon") is True

    def test_is_available_when_open(self, breaker, mock_redis):
        """Test that requests are blocked when circuit is OPEN."""
        mock_redis.get.side_effect = [
            CircuitBreaker.STATE_OPEN,  # Initial state check
            datetime.utcnow().isoformat(),  # Last failure timestamp (recent)
        ]
        assert breaker.is_available("amazon") is False

    def test_is_available_transitions_to_half_open(self, breaker, mock_redis):
        """Test that circuit transitions to HALF_OPEN after recovery timeout."""
        # Circuit is OPEN but recovery timeout has passed
        past_time = (datetime.utcnow() - timedelta(seconds=120)).isoformat()
        mock_redis.get.side_effect = [
            CircuitBreaker.STATE_OPEN,  # Initial state
            past_time,  # Last failure (> recovery_timeout)
        ]

        assert breaker.is_available("amazon") is True
        # Should have set state to HALF_OPEN
        mock_redis.set.assert_called()

    def test_record_success_in_closed_state(self, breaker, mock_redis):
        """Test recording success in CLOSED state resets failure counter."""
        mock_redis.get.return_value = CircuitBreaker.STATE_CLOSED

        breaker.record_success("amazon")
        mock_redis.set.assert_called()  # Should reset failure counter

    def test_record_success_in_half_open_closes_circuit(self, breaker, mock_redis):
        """Test that enough successes in HALF_OPEN closes circuit."""
        mock_redis.get.return_value = CircuitBreaker.STATE_HALF_OPEN
        mock_redis.incr.side_effect = [1, 2]  # 2 successes

        breaker.record_success("amazon")  # First success
        breaker.record_success("amazon")  # Second success (should close)

        # Should have closed the circuit
        calls = [call[0][1] for call in mock_redis.set.call_args_list if call[0][1] == CircuitBreaker.STATE_CLOSED]
        assert len(calls) > 0

    def test_record_failure_increments_counter(self, breaker, mock_redis):
        """Test that record_failure increments failure counter."""
        mock_redis.get.return_value = CircuitBreaker.STATE_CLOSED
        mock_redis.incr.return_value = 1

        breaker.record_failure("amazon")
        mock_redis.incr.assert_called()

    def test_record_failure_opens_circuit_at_threshold(self, breaker, mock_redis):
        """Test that circuit opens when failure threshold is reached."""
        mock_redis.get.return_value = CircuitBreaker.STATE_CLOSED
        mock_redis.incr.return_value = 10  # Reached threshold (10 for Amazon)

        breaker.record_failure("amazon")

        # Should have opened the circuit
        calls = [call[0][1] for call in mock_redis.set.call_args_list if call[0][1] == CircuitBreaker.STATE_OPEN]
        assert len(calls) > 0

    def test_record_failure_in_half_open_reopens_circuit(self, breaker, mock_redis):
        """Test that failure in HALF_OPEN immediately reopens circuit."""
        mock_redis.get.return_value = CircuitBreaker.STATE_HALF_OPEN

        breaker.record_failure("amazon")

        # Should have opened the circuit
        calls = [call[0][1] for call in mock_redis.set.call_args_list if call[0][1] == CircuitBreaker.STATE_OPEN]
        assert len(calls) > 0

    def test_reset_clears_all_data(self, breaker, mock_redis):
        """Test that reset clears all circuit breaker data."""
        breaker.reset("amazon")

        # Should have deleted all keys
        assert mock_redis.delete.call_count >= 3


@pytest.mark.unit
class TestProxyRotator:
    """Test proxy rotation functionality."""

    def test_init_with_proxy_list(self):
        """Test initialization with proxy list."""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        rotator = ProxyRotator(proxy_list=proxies)
        assert rotator.enabled is True
        assert len(rotator.proxy_list) == 2

    def test_init_without_proxies(self):
        """Test initialization without proxies."""
        rotator = ProxyRotator(proxy_list=[])
        assert rotator.enabled is False

    def test_get_next_rotates_proxies(self):
        """Test that get_next rotates through proxy list."""
        proxies = ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]
        rotator = ProxyRotator(proxy_list=proxies)

        p1 = rotator.get_next()
        p2 = rotator.get_next()
        p3 = rotator.get_next()
        p4 = rotator.get_next()  # Should wrap around

        assert p1 == "http://proxy1:8080"
        assert p2 == "http://proxy2:8080"
        assert p3 == "http://proxy3:8080"
        assert p4 == "http://proxy1:8080"  # Back to first

    def test_get_next_returns_none_when_disabled(self):
        """Test that get_next returns None when no proxies."""
        rotator = ProxyRotator(proxy_list=[])
        assert rotator.get_next() is None

    def test_get_random_returns_proxy(self):
        """Test that get_random returns a proxy from list."""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        rotator = ProxyRotator(proxy_list=proxies)

        proxy = rotator.get_random()
        assert proxy in proxies

    def test_get_random_returns_none_when_disabled(self):
        """Test that get_random returns None when no proxies."""
        rotator = ProxyRotator(proxy_list=[])
        assert rotator.get_random() is None

    def test_get_proxies_dict_format(self):
        """Test that get_proxies_dict returns correct format."""
        proxies = ["http://proxy1:8080"]
        rotator = ProxyRotator(proxy_list=proxies)

        proxies_dict = rotator.get_proxies_dict()
        assert proxies_dict is not None
        assert "http" in proxies_dict
        assert "https" in proxies_dict
        assert proxies_dict["http"] == "http://proxy1:8080"
        assert proxies_dict["https"] == "http://proxy1:8080"

    def test_get_proxies_dict_returns_none_when_disabled(self):
        """Test that get_proxies_dict returns None when no proxies."""
        rotator = ProxyRotator(proxy_list=[])
        assert rotator.get_proxies_dict() is None

    def test_add_proxy(self):
        """Test adding a new proxy to rotation."""
        rotator = ProxyRotator(proxy_list=[])
        assert rotator.enabled is False

        rotator.add_proxy("http://newproxy:8080")
        assert rotator.enabled is True
        assert len(rotator.proxy_list) == 1
        assert "http://newproxy:8080" in rotator.proxy_list

    def test_add_proxy_prevents_duplicates(self):
        """Test that add_proxy doesn't add duplicates."""
        proxies = ["http://proxy1:8080"]
        rotator = ProxyRotator(proxy_list=proxies)

        rotator.add_proxy("http://proxy1:8080")
        assert len(rotator.proxy_list) == 1

    def test_remove_proxy(self):
        """Test removing a proxy from rotation."""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        rotator = ProxyRotator(proxy_list=proxies)

        rotator.remove_proxy("http://proxy1:8080")
        assert len(rotator.proxy_list) == 1
        assert "http://proxy1:8080" not in rotator.proxy_list

    def test_remove_proxy_disables_when_empty(self):
        """Test that removing last proxy disables rotation."""
        proxies = ["http://proxy1:8080"]
        rotator = ProxyRotator(proxy_list=proxies)
        assert rotator.enabled is True

        rotator.remove_proxy("http://proxy1:8080")
        assert rotator.enabled is False
