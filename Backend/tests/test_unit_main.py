"""
Unit tests for FastAPI main application.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestMainApp:
    """Test suite for main FastAPI application."""

    def test_root_endpoint(self):
        """Test root endpoint returns welcome message."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome to PriceWatch API" in data["message"]
        assert "version" in data
        assert "docs" in data

    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is configured."""
        from app.main import app
        from fastapi.middleware.cors import CORSMiddleware

        # Check that CORS middleware is added
        middleware_types = [type(m) for m in app.user_middleware]
        # In FastAPI, middleware is wrapped, so we check if any middleware contains CORS
        assert any("CORS" in str(m) for m in app.user_middleware)

    def test_app_has_auth_router(self):
        """Test that auth router is included."""
        from app.main import app

        # Check that routes exist
        routes = [route.path for route in app.routes]
        assert any("/auth/" in route for route in routes)

    def test_app_has_products_router(self):
        """Test that products router is included."""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("/products" in route for route in routes)

    def test_app_has_preferences_router(self):
        """Test that preferences router is included."""
        from app.main import app

        routes = [route.path for route in app.routes]
        assert any("/users" in route for route in routes)

    def test_app_title(self):
        """Test that app has correct title."""
        from app.main import app
        from app.core.config import settings

        assert app.title == settings.PROJECT_NAME

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoint_available(self):
        """Test that Swagger docs endpoint is available."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_endpoint_available(self):
        """Test that ReDoc endpoint is available."""
        from app.main import app

        client = TestClient(app)
        response = client.get("/redoc")

        assert response.status_code == 200
