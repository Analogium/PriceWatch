"""
Health check endpoints for monitoring application and infrastructure health.
Provides detailed status for database, Redis, and Celery components.
"""

from datetime import datetime
from typing import Any, Dict

import redis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.logging_config import get_logger
from tasks import celery_app

router = APIRouter()
logger = get_logger(__name__)


def check_database(db: Session) -> Dict[str, Any]:
    """Check database connectivity and basic stats."""
    try:
        # Test connection with simple query
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            # Get database version
            version_result = db.execute(text("SELECT version()")).fetchone()
            db_version = version_result[0] if version_result else "Unknown"

            # Get table count
            table_count_result = db.execute(
                text("SELECT count(*) FROM information_schema.tables " "WHERE table_schema = 'public'")
            ).fetchone()
            table_count = table_count_result[0] if table_count_result else 0

            return {
                "status": "healthy",
                "latency_ms": 0,  # Could add timing
                "version": db_version,
                "tables": table_count,
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Database query returned unexpected result",
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and basic stats."""
    try:
        # Parse Redis URL
        redis_client = redis.from_url(settings.REDIS_URL)

        # Test connection
        ping_result = redis_client.ping()
        if ping_result:
            # Get Redis info
            info = redis_client.info()

            return {
                "status": "healthy",
                "version": info.get("redis_version", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "Unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Database query returned unexpected result",
            }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def check_celery() -> Dict[str, Any]:
    """Check Celery worker status and queue info."""
    try:
        # Control is accessed via celery_app.control

        # Get active workers (with timeout)
        inspect = celery_app.control.inspect(timeout=2.0)
        active_workers = inspect.active()

        if active_workers is None:
            return {
                "status": "unhealthy",
                "error": "No active workers found",
                "workers": 0,
            }

        worker_count = len(active_workers)

        # Get registered tasks from workers
        registered = inspect.registered()
        tasks = []
        if registered:
            for worker_tasks in registered.values():
                tasks.extend(worker_tasks)
            tasks = list(set(tasks))  # Remove duplicates

        # Get scheduled tasks (Beat schedule)
        scheduled_tasks = list(celery_app.conf.beat_schedule.keys())

        return {
            "status": "healthy",
            "workers": worker_count,
            "active_workers": list(active_workers.keys()),
            "registered_tasks": len(tasks),
            "scheduled_tasks": scheduled_tasks,
        }

    except Exception as e:
        logger.error(f"Celery health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "workers": 0,
        }


@router.get("/")
def basic_health():
    """Basic health check - returns healthy if API is responding."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "pricewatch-api",
    }


@router.get("/detailed")
def detailed_health(db: Session = Depends(get_db)):
    """
    Detailed health check for all components.

    Returns status of:
    - API server
    - PostgreSQL database
    - Redis cache/broker
    - Celery workers
    """
    timestamp = datetime.utcnow().isoformat()

    # Check all components
    database_status = check_database(db)
    redis_status = check_redis()
    celery_status = check_celery()

    # Determine overall health
    all_healthy = all(
        [
            database_status.get("status") == "healthy",
            redis_status.get("status") == "healthy",
            celery_status.get("status") == "healthy",
        ]
    )

    response = {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": timestamp,
        "service": "pricewatch-api",
        "version": "1.0.0",
        "components": {
            "database": database_status,
            "redis": redis_status,
            "celery": celery_status,
        },
    }

    if not all_healthy:
        logger.warning(f"Health check degraded: {response}")

    return response


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness probe.
    Returns 200 if the service is ready to receive traffic.
    Checks database and Redis (required for basic operations).
    """
    database_status = check_database(db)
    redis_status = check_redis()

    is_ready = database_status.get("status") == "healthy" and redis_status.get("status") == "healthy"

    if not is_ready:
        # Return 503 Service Unavailable for k8s to understand
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": database_status,
                "redis": redis_status,
            },
        )

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
def liveness_check():
    """
    Kubernetes-style liveness probe.
    Returns 200 if the service process is alive.
    This is a simple check that doesn't verify dependencies.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
