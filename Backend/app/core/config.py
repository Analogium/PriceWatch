from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "PriceWatch"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None

    # Password Policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL_CHAR: bool = True

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    FRONTEND_URL: str = "http://localhost:5173"  # Frontend URL for email links

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Optional[str] = "./logs"
    ENABLE_JSON_LOGS: bool = False
    ENABLE_LOG_ROTATION: bool = True

    # Scraping Parallelization
    MAX_PARALLEL_SCRAPERS: int = 5  # Maximum number of concurrent scrapers
    SCRAPING_BATCH_SIZE: int = 10  # Number of products to scrape in parallel batches

    # Scraping Advanced Features
    SCRAPER_CACHE_ENABLED: bool = True  # Enable Redis cache for scraping results
    SCRAPER_CACHE_TTL: int = 3600  # Cache TTL in seconds (default: 1 hour)
    SCRAPER_CIRCUIT_BREAKER_ENABLED: bool = True  # Enable circuit breaker pattern
    SCRAPER_CIRCUIT_BREAKER_THRESHOLD: int = 5  # Failures before opening circuit
    SCRAPER_CIRCUIT_BREAKER_TIMEOUT: int = 60  # Seconds before attempting recovery
    SCRAPER_PROXY_ENABLED: bool = False  # Enable proxy rotation
    PROXY_LIST: str = ""  # Comma or newline-separated list of proxy URLs

    # Sentry Error Monitoring
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions traced
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1  # 10% of transactions profiled

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]
