"""
Advanced scraping utilities: User-Agent rotation, caching, circuit breaker, and proxy support.
"""

import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from redis import Redis

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UserAgentRotator:
    """Rotates User-Agent headers to avoid detection and blocking."""

    # Site-specific referers to appear as legitimate traffic
    REFERERS = {
        "amazon": [
            "https://www.google.fr/search?q=amazon",
            "https://www.google.fr/",
            "https://www.amazon.fr/",
        ],
        "fnac": [
            "https://www.google.fr/search?q=fnac",
            "https://www.google.fr/",
            "https://www.fnac.com/",
        ],
        "cdiscount": [
            "https://www.google.fr/search?q=cdiscount",
            "https://www.google.fr/",
        ],
        "darty": [
            "https://www.google.fr/search?q=darty",
            "https://www.google.fr/",
        ],
        "boulanger": [
            "https://www.google.fr/search?q=boulanger",
            "https://www.google.fr/",
        ],
        "leclerc": [
            "https://www.google.fr/search?q=leclerc",
            "https://www.google.fr/",
        ],
        "default": [
            "https://www.google.fr/",
        ],
    }

    # Comprehensive list of realistic User-Agents (browsers from 2023-2024)
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    @classmethod
    def get_random(cls) -> str:
        """
        Get a random User-Agent string.

        Returns:
            Random User-Agent string from the pool
        """
        user_agent = random.choice(cls.USER_AGENTS)
        logger.debug(f"Selected User-Agent: {user_agent[:50]}...")
        return user_agent

    @classmethod
    def get_headers(cls, site: str = "default", include_full_headers: bool = True) -> Dict[str, str]:
        """
        Get a complete set of HTTP headers with random User-Agent and site-specific Referer.

        Args:
            site: Target site name for site-specific headers (e.g., 'amazon', 'fnac')
            include_full_headers: If True, includes all browser headers. If False, only User-Agent.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "User-Agent": cls.get_random(),
        }

        if include_full_headers:
            referers = cls.REFERERS.get(site, cls.REFERERS["default"])
            headers.update(
                {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": random.choice(referers),
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "cross-site",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                }
            )

        logger.debug(f"Generated headers for site '{site}' with {len(headers)} fields")
        return headers


class ScraperCache:
    """Redis-based cache for scraping results to avoid redundant requests."""

    def __init__(self, redis_client: Optional[Redis] = None, default_ttl: int = 3600):
        """
        Initialize scraper cache.

        Args:
            redis_client: Redis client instance (if None, will create from settings)
            default_ttl: Default cache TTL in seconds (default: 1 hour)
        """
        if redis_client is not None:
            self.redis_client: Redis = redis_client
        else:
            self.redis_client = Redis.from_url(  # type: ignore[assignment,no-redef]
                settings.REDIS_URL, decode_responses=True
            )
        self.default_ttl = default_ttl
        self.key_prefix = "scraper_cache:"
        logger.info(f"ScraperCache initialized with TTL={default_ttl}s")

    def _generate_cache_key(self, url: str) -> str:
        """
        Generate a unique cache key for a URL.

        Args:
            url: Product URL

        Returns:
            Cache key string
        """
        # Use MD5 hash of URL to create consistent key
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{self.key_prefix}{url_hash}"

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached scraping result for a URL.

        Args:
            url: Product URL

        Returns:
            Cached data dictionary or None if not found/expired
        """
        try:
            cache_key = self._generate_cache_key(url)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                logger.info(f"Cache HIT for URL: {url[:60]}...")
                # Redis decode_responses=True ensures cached_data is str
                return json.loads(str(cached_data))
            else:
                logger.debug(f"Cache MISS for URL: {url[:60]}...")
                return None

        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None

    def set(self, url: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Cache scraping result for a URL.

        Args:
            url: Product URL
            data: Scraped data to cache
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(url)
            ttl = ttl or self.default_ttl

            # Add timestamp to cached data
            data_with_meta = {
                **data,
                "cached_at": datetime.utcnow().isoformat(),
            }

            self.redis_client.setex(cache_key, ttl, json.dumps(data_with_meta))
            logger.info(f"Cached result for URL (TTL={ttl}s): {url[:60]}...")
            return True

        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")
            return False

    def invalidate(self, url: str) -> bool:
        """
        Invalidate (delete) cached result for a URL.

        Args:
            url: Product URL

        Returns:
            True if cache entry was deleted, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(url)
            deleted = self.redis_client.delete(cache_key)
            if deleted:
                logger.info(f"Invalidated cache for URL: {url[:60]}...")
            return bool(deleted)

        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return False

    def clear_all(self) -> int:
        """
        Clear all scraper cache entries.

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = list(self.redis_client.scan_iter(match=pattern))
            if keys:
                deleted = self.redis_client.delete(*keys)  # type: ignore[arg-type]
                deleted_count = int(deleted)  # type: ignore[arg-type]
                logger.info(f"Cleared {deleted_count} cache entries")
                return deleted_count
            return 0

        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return 0


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent overwhelming e-commerce sites.

    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    # Site-specific thresholds (Amazon needs higher threshold due to frequent CAPTCHAs)
    SITE_THRESHOLDS = {
        "amazon": {"failure_threshold": 10, "recovery_timeout": 120},
        "cdiscount": {"failure_threshold": 8, "recovery_timeout": 90},
        "default": {"failure_threshold": 5, "recovery_timeout": 60},
    }

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker.

        Args:
            redis_client: Redis client for distributed state
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            success_threshold: Consecutive successes needed to close circuit from half-open
        """
        if redis_client is not None:
            self.redis_client: Redis = redis_client
        else:
            self.redis_client = Redis.from_url(  # type: ignore[assignment,no-redef]
                settings.REDIS_URL, decode_responses=True
            )
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.key_prefix = "circuit_breaker:"
        logger.info(
            f"CircuitBreaker initialized (failure_threshold={failure_threshold}, "
            f"recovery_timeout={recovery_timeout}s)"
        )

    def _get_state_key(self, site: str) -> str:
        """Get Redis key for circuit state."""
        return f"{self.key_prefix}{site}:state"

    def _get_failure_key(self, site: str) -> str:
        """Get Redis key for failure count."""
        return f"{self.key_prefix}{site}:failures"

    def _get_success_key(self, site: str) -> str:
        """Get Redis key for success count (in half-open state)."""
        return f"{self.key_prefix}{site}:successes"

    def _get_last_failure_key(self, site: str) -> str:
        """Get Redis key for last failure timestamp."""
        return f"{self.key_prefix}{site}:last_failure"

    def _get_site_thresholds(self, site: str) -> Dict[str, int]:
        """Get failure threshold and recovery timeout for a specific site."""
        return self.SITE_THRESHOLDS.get(site, self.SITE_THRESHOLDS["default"])

    def get_state(self, site: str) -> str:
        """
        Get current circuit state for a site.

        Args:
            site: Site name (e.g., 'amazon', 'fnac')

        Returns:
            Circuit state: CLOSED, OPEN, or HALF_OPEN
        """
        try:
            state = self.redis_client.get(self._get_state_key(site))
            return str(state) if state else self.STATE_CLOSED
        except Exception as e:
            logger.error(f"Error getting circuit state: {str(e)}")
            return self.STATE_CLOSED

    def is_available(self, site: str) -> bool:
        """
        Check if requests are allowed for a site.

        Args:
            site: Site name

        Returns:
            True if requests allowed, False if circuit is open
        """
        state = self.get_state(site)
        site_thresholds = self._get_site_thresholds(site)
        recovery_timeout = site_thresholds["recovery_timeout"]

        if state == self.STATE_CLOSED:
            return True

        if state == self.STATE_OPEN:
            # Check if recovery timeout has passed (use site-specific timeout)
            try:
                last_failure_ts = self.redis_client.get(self._get_last_failure_key(site))
                if last_failure_ts:
                    last_failure = datetime.fromisoformat(str(last_failure_ts))
                    if datetime.utcnow() >= last_failure + timedelta(seconds=recovery_timeout):
                        # Move to half-open state
                        logger.info(f"Circuit for '{site}' moving to HALF_OPEN state (recovery attempt)")
                        self.redis_client.set(self._get_state_key(site), self.STATE_HALF_OPEN)
                        self.redis_client.set(self._get_success_key(site), 0)
                        return True
            except Exception as e:
                logger.error(f"Error checking recovery timeout: {str(e)}")

            logger.warning(f"Circuit OPEN for '{site}' - requests blocked (recovery in {recovery_timeout}s)")
            return False

        # HALF_OPEN state - allow limited requests
        return True

    def record_success(self, site: str) -> None:
        """
        Record a successful request.

        Args:
            site: Site name
        """
        try:
            state = self.get_state(site)

            if state == self.STATE_HALF_OPEN:
                # Increment success counter
                successes = int(self.redis_client.incr(self._get_success_key(site)))  # type: ignore[arg-type]
                logger.info(f"Circuit HALF_OPEN for '{site}': {successes}/{self.success_threshold} successes")

                if successes >= self.success_threshold:
                    # Close circuit - service recovered
                    logger.info(f"Circuit CLOSED for '{site}' - service recovered")
                    self.redis_client.set(self._get_state_key(site), self.STATE_CLOSED)
                    self.redis_client.delete(self._get_failure_key(site))
                    self.redis_client.delete(self._get_success_key(site))
                    self.redis_client.delete(self._get_last_failure_key(site))

            elif state == self.STATE_CLOSED:
                # Reset failure counter on success
                self.redis_client.set(self._get_failure_key(site), 0)

        except Exception as e:
            logger.error(f"Error recording success: {str(e)}")

    def record_failure(self, site: str) -> None:
        """
        Record a failed request.

        Args:
            site: Site name
        """
        try:
            state = self.get_state(site)
            site_thresholds = self._get_site_thresholds(site)
            failure_threshold = site_thresholds["failure_threshold"]

            # Increment failure counter
            failures = int(self.redis_client.incr(self._get_failure_key(site)))  # type: ignore[arg-type]
            self.redis_client.set(
                self._get_last_failure_key(site),
                datetime.utcnow().isoformat(),
            )

            logger.warning(f"Circuit failure for '{site}': {failures}/{failure_threshold}")

            if state == self.STATE_HALF_OPEN:
                # Immediate open on failure during recovery
                logger.warning(f"Circuit OPEN for '{site}' - recovery failed")
                self.redis_client.set(self._get_state_key(site), self.STATE_OPEN)
                self.redis_client.delete(self._get_success_key(site))

            elif failures >= failure_threshold:
                # Open circuit
                logger.warning(f"Circuit OPEN for '{site}' - threshold reached ({failures} failures)")
                self.redis_client.set(self._get_state_key(site), self.STATE_OPEN)

        except Exception as e:
            logger.error(f"Error recording failure: {str(e)}")

    def reset(self, site: str) -> None:
        """
        Reset circuit breaker for a site (manual recovery).

        Args:
            site: Site name
        """
        try:
            logger.info(f"Manually resetting circuit for '{site}'")
            self.redis_client.delete(self._get_state_key(site))
            self.redis_client.delete(self._get_failure_key(site))
            self.redis_client.delete(self._get_success_key(site))
            self.redis_client.delete(self._get_last_failure_key(site))
        except Exception as e:
            logger.error(f"Error resetting circuit: {str(e)}")


class ProxyRotator:
    """Rotates proxy servers to avoid IP-based blocking."""

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize proxy rotator.

        Args:
            proxy_list: List of proxy URLs (format: "http://ip:port" or "http://user:pass@ip:port")
                       If None, reads from settings.PROXY_LIST
        """
        self.proxy_list = proxy_list or self._load_proxies_from_settings()
        self.current_index = 0
        self.enabled = len(self.proxy_list) > 0

        if self.enabled:
            logger.info(f"ProxyRotator initialized with {len(self.proxy_list)} proxies")
        else:
            logger.info("ProxyRotator initialized with no proxies (disabled)")

    def _load_proxies_from_settings(self) -> List[str]:
        """
        Load proxy list from settings.

        Returns:
            List of proxy URLs
        """
        try:
            proxy_str = getattr(settings, "PROXY_LIST", "")
            if proxy_str:
                # Split by comma or newline
                proxies = [p.strip() for p in proxy_str.replace("\n", ",").split(",")]
                return [p for p in proxies if p]  # Remove empty strings
            return []
        except Exception as e:
            logger.error(f"Error loading proxies from settings: {str(e)}")
            return []

    def get_next(self) -> Optional[str]:
        """
        Get next proxy from rotation.

        Returns:
            Proxy URL or None if no proxies available
        """
        if not self.enabled:
            return None

        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)

        logger.debug(f"Selected proxy: {proxy}")
        return proxy

    def get_random(self) -> Optional[str]:
        """
        Get random proxy from list.

        Returns:
            Random proxy URL or None if no proxies available
        """
        if not self.enabled:
            return None

        proxy = random.choice(self.proxy_list)
        logger.debug(f"Selected random proxy: {proxy}")
        return proxy

    def get_proxies_dict(self, random_selection: bool = False) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration dictionary for requests library.

        Args:
            random_selection: If True, uses random proxy. If False, uses rotation.

        Returns:
            Proxies dict {"http": proxy, "https": proxy} or None
        """
        proxy = self.get_random() if random_selection else self.get_next()
        if proxy:
            return {"http": proxy, "https": proxy}
        return None

    def add_proxy(self, proxy_url: str) -> None:
        """
        Add a new proxy to the rotation.

        Args:
            proxy_url: Proxy URL to add
        """
        if proxy_url not in self.proxy_list:
            self.proxy_list.append(proxy_url)
            self.enabled = True
            logger.info(f"Added proxy: {proxy_url} (total: {len(self.proxy_list)})")

    def remove_proxy(self, proxy_url: str) -> None:
        """
        Remove a proxy from rotation.

        Args:
            proxy_url: Proxy URL to remove
        """
        if proxy_url in self.proxy_list:
            self.proxy_list.remove(proxy_url)
            self.enabled = len(self.proxy_list) > 0
            logger.info(f"Removed proxy: {proxy_url} (remaining: {len(self.proxy_list)})")
