"""
Unit tests for health check endpoints.
Tests all health check functionality with mocked dependencies.
"""

# datetime not needed
from unittest.mock import Mock, patch

import pytest

from app.api.endpoints.health import (
    basic_health,
    check_celery,
    check_database,
    check_redis,
    detailed_health,
    liveness_check,
    readiness_check,
)


@pytest.mark.unit
class TestCheckDatabase:
    """Tests for the check_database function."""

    def test_database_healthy(self):
        """Test database health check when database is healthy."""
        mock_db = Mock()

        # Mock successful query results
        mock_db.execute.return_value.fetchone.side_effect = [
            (1,),  # SELECT 1
            ("PostgreSQL 15.0",),  # SELECT version()
            (5,),  # Table count
        ]

        result = check_database(mock_db)

        assert result["status"] == "healthy"
        assert "PostgreSQL 15.0" in result["version"]
        assert result["tables"] == 5

    def test_database_unhealthy(self):
        """Test database health check when database connection fails."""
        mock_db = Mock()
        mock_db.execute.side_effect = Exception("Connection refused")

        result = check_database(mock_db)

        assert result["status"] == "unhealthy"
        assert "Connection refused" in result["error"]

    def test_database_query_fails(self):
        """Test database health check when query returns None."""
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = None

        result = check_database(mock_db)

        assert result["status"] == "unhealthy"


@pytest.mark.unit
class TestCheckRedis:
    """Tests for the check_redis function."""

    @patch("app.api.endpoints.health.redis.from_url")
    def test_redis_healthy(self, mock_from_url):
        """Test Redis health check when Redis is healthy."""
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.info.return_value = {
            "redis_version": "7.0.0",
            "connected_clients": 5,
            "used_memory_human": "1.5M",
            "uptime_in_seconds": 86400,
        }

        result = check_redis()

        assert result["status"] == "healthy"
        assert result["version"] == "7.0.0"
        assert result["connected_clients"] == 5
        assert result["used_memory_human"] == "1.5M"

    @patch("app.api.endpoints.health.redis.from_url")
    def test_redis_unhealthy(self, mock_from_url):
        """Test Redis health check when Redis connection fails."""
        mock_from_url.side_effect = Exception("Connection refused")

        result = check_redis()

        assert result["status"] == "unhealthy"
        assert "Connection refused" in result["error"]

    @patch("app.api.endpoints.health.redis.from_url")
    def test_redis_ping_fails(self, mock_from_url):
        """Test Redis health check when ping fails."""
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        mock_client.ping.side_effect = Exception("Ping failed")

        result = check_redis()

        assert result["status"] == "unhealthy"


@pytest.mark.unit
class TestCheckCelery:
    """Tests for the check_celery function."""

    @patch("app.api.endpoints.health.celery_app")
    def test_celery_healthy(self, mock_celery):
        """Test Celery health check when workers are healthy."""
        mock_inspect = Mock()
        mock_celery.control.inspect.return_value = mock_inspect

        # Mock active workers
        mock_inspect.active.return_value = {
            "worker1@host": [],
            "worker2@host": [],
        }

        # Mock registered tasks
        mock_inspect.registered.return_value = {
            "worker1@host": ["check_all_prices", "check_single_product"],
        }

        # Mock beat schedule
        mock_celery.conf.beat_schedule = {
            "check-prices-6h": {},
            "check-prices-12h": {},
        }

        result = check_celery()

        assert result["status"] == "healthy"
        assert result["workers"] == 2
        assert len(result["active_workers"]) == 2
        assert result["registered_tasks"] == 2

    @patch("app.api.endpoints.health.celery_app")
    def test_celery_no_workers(self, mock_celery):
        """Test Celery health check when no workers are available."""
        mock_inspect = Mock()
        mock_celery.control.inspect.return_value = mock_inspect
        mock_inspect.active.return_value = None

        result = check_celery()

        assert result["status"] == "unhealthy"
        assert "No active workers found" in result["error"]
        assert result["workers"] == 0

    @patch("app.api.endpoints.health.celery_app")
    def test_celery_connection_error(self, mock_celery):
        """Test Celery health check when connection fails."""
        mock_celery.control.inspect.side_effect = Exception("Broker unreachable")

        result = check_celery()

        assert result["status"] == "unhealthy"
        assert "Broker unreachable" in result["error"]


@pytest.mark.unit
class TestBasicHealth:
    """Tests for the basic_health endpoint."""

    def test_basic_health_returns_healthy(self):
        """Test basic health check returns healthy status."""
        result = basic_health()

        assert result["status"] == "healthy"
        assert result["service"] == "pricewatch-api"
        assert "timestamp" in result


@pytest.mark.unit
class TestDetailedHealth:
    """Tests for the detailed_health endpoint."""

    @patch("app.api.endpoints.health.check_celery")
    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_detailed_health_all_healthy(self, mock_db, mock_redis, mock_celery):
        """Test detailed health when all components are healthy."""
        mock_db.return_value = {"status": "healthy", "version": "PostgreSQL 15"}
        mock_redis.return_value = {"status": "healthy", "version": "7.0"}
        mock_celery.return_value = {"status": "healthy", "workers": 2}

        mock_session = Mock()
        result = detailed_health(mock_session)

        assert result["status"] == "healthy"
        assert result["components"]["database"]["status"] == "healthy"
        assert result["components"]["redis"]["status"] == "healthy"
        assert result["components"]["celery"]["status"] == "healthy"

    @patch("app.api.endpoints.health.check_celery")
    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_detailed_health_degraded(self, mock_db, mock_redis, mock_celery):
        """Test detailed health when some components are unhealthy."""
        mock_db.return_value = {"status": "healthy", "version": "PostgreSQL 15"}
        mock_redis.return_value = {"status": "unhealthy", "error": "Connection refused"}
        mock_celery.return_value = {"status": "healthy", "workers": 2}

        mock_session = Mock()
        result = detailed_health(mock_session)

        assert result["status"] == "degraded"
        assert result["components"]["database"]["status"] == "healthy"
        assert result["components"]["redis"]["status"] == "unhealthy"

    @patch("app.api.endpoints.health.check_celery")
    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_detailed_health_all_unhealthy(self, mock_db, mock_redis, mock_celery):
        """Test detailed health when all components are unhealthy."""
        mock_db.return_value = {"status": "unhealthy", "error": "DB error"}
        mock_redis.return_value = {"status": "unhealthy", "error": "Redis error"}
        mock_celery.return_value = {"status": "unhealthy", "error": "Celery error"}

        mock_session = Mock()
        result = detailed_health(mock_session)

        assert result["status"] == "degraded"


@pytest.mark.unit
class TestReadinessCheck:
    """Tests for the readiness_check endpoint."""

    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_readiness_ready(self, mock_db, mock_redis):
        """Test readiness check when system is ready."""
        mock_db.return_value = {"status": "healthy"}
        mock_redis.return_value = {"status": "healthy"}

        mock_session = Mock()
        result = readiness_check(mock_session)

        assert result["status"] == "ready"
        assert "timestamp" in result

    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_readiness_not_ready_db_down(self, mock_db, mock_redis):
        """Test readiness check when database is down."""
        from fastapi import HTTPException

        mock_db.return_value = {"status": "unhealthy", "error": "DB error"}
        mock_redis.return_value = {"status": "healthy"}

        mock_session = Mock()

        with pytest.raises(HTTPException) as exc_info:
            readiness_check(mock_session)

        assert exc_info.value.status_code == 503

    @patch("app.api.endpoints.health.check_redis")
    @patch("app.api.endpoints.health.check_database")
    def test_readiness_not_ready_redis_down(self, mock_db, mock_redis):
        """Test readiness check when Redis is down."""
        from fastapi import HTTPException

        mock_db.return_value = {"status": "healthy"}
        mock_redis.return_value = {"status": "unhealthy", "error": "Redis error"}

        mock_session = Mock()

        with pytest.raises(HTTPException) as exc_info:
            readiness_check(mock_session)

        assert exc_info.value.status_code == 503


@pytest.mark.unit
class TestLivenessCheck:
    """Tests for the liveness_check endpoint."""

    def test_liveness_alive(self):
        """Test liveness check returns alive status."""
        result = liveness_check()

        assert result["status"] == "alive"
        assert "timestamp" in result


@pytest.mark.unit
class TestHealthEndpointIntegration:
    """Integration-style tests for health endpoints with FastAPI TestClient."""

    @patch("app.api.endpoints.health.celery_app")
    @patch("app.api.endpoints.health.redis.from_url")
    def test_health_endpoint_with_test_client(self, mock_redis, mock_celery):
        """Test health endpoints work with FastAPI TestClient."""
        from fastapi.testclient import TestClient

        from app.main import app

        # Setup mocks
        mock_client = Mock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.info.return_value = {
            "redis_version": "7.0.0",
            "connected_clients": 1,
            "used_memory_human": "1M",
            "uptime_in_seconds": 100,
        }

        mock_inspect = Mock()
        mock_celery.control.inspect.return_value = mock_inspect
        mock_inspect.active.return_value = {"worker1": []}
        mock_inspect.registered.return_value = {"worker1": ["task1"]}
        mock_celery.conf.beat_schedule = {"task": {}}

        client = TestClient(app)

        # Test basic health
        response = client.get("/health/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # Test liveness
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
