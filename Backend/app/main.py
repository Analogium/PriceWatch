from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, products, preferences
from app.db.base import Base, engine
from app.core.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=settings.LOG_DIR,
    enable_json=settings.ENABLE_JSON_LOGS,
    enable_rotation=settings.ENABLE_LOG_ROTATION,
)

logger = get_logger(__name__)
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


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to PriceWatch API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
