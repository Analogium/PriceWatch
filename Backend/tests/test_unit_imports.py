"""
Unit tests for module imports and basic functionality.
"""

import pytest


@pytest.mark.unit
class TestImports:
    """Test suite for verifying imports work correctly."""

    def test_import_models(self):
        """Test that all models can be imported."""
        from app.models import price_history, product, user, user_preferences

        assert user.User is not None
        assert product.Product is not None
        assert price_history.PriceHistory is not None
        assert user_preferences.UserPreferences is not None

    def test_import_schemas(self):
        """Test that all schemas can be imported."""
        from app.schemas import price_history, product, user, user_preferences

        assert user.UserCreate is not None
        assert product.ProductCreate is not None
        assert price_history.PriceHistoryResponse is not None
        assert user_preferences.UserPreferencesUpdate is not None

    def test_import_services(self):
        """Test that all services can be imported."""
        from app.services import email, price_history, scraper

        assert email.EmailService is not None
        assert scraper.PriceScraper is not None
        assert price_history.PriceHistoryService is not None

    def test_import_api_endpoints(self):
        """Test that API endpoints can be imported."""
        from app.api.endpoints import auth, preferences, products

        assert auth.router is not None
        assert products.router is not None
        assert preferences.router is not None

    def test_import_core_modules(self):
        """Test that core modules can be imported."""
        from app.core import config, logging_config, rate_limit, security

        assert config.settings is not None
        assert security.get_password_hash is not None
        assert rate_limit.RateLimiter is not None
        assert logging_config.setup_logging is not None

    def test_app_main_imports(self):
        """Test main app can be imported."""
        from app import main

        assert main.app is not None
        assert main.logger is not None
