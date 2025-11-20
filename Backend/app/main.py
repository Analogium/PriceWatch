from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import admin, auth, health, preferences, products
from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.db.base import Base, engine

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=settings.LOG_DIR,
    enable_json=settings.ENABLE_JSON_LOGS,
    enable_rotation=settings.ENABLE_LOG_ROTATION,
)

logger = get_logger(__name__)

# Initialize Sentry for error monitoring
if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            send_default_pii=False,  # Don't send PII data
        )
        logger.info(f"Sentry initialized for environment: {settings.SENTRY_ENVIRONMENT}")
    except ImportError:
        logger.warning("sentry-sdk not installed. Error monitoring disabled.")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {str(e)}")
else:
    logger.info("Sentry DSN not configured. Error monitoring disabled.")

logger.info("Starting PriceWatch API application")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(products.router, prefix=f"{settings.API_V1_PREFIX}/products", tags=["Products"])
app.include_router(preferences.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["User Preferences"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Administration"])
app.include_router(health.router, prefix="/health", tags=["Health"])


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to PriceWatch API", "version": "1.0.0", "docs": "/docs"}
