"""
Unit tests for product endpoints.
Tests product creation with price alerts.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.product import ProductCreate


@pytest.mark.unit
class TestCreateProductWithAlert:
    """Test suite for product creation with price alerts."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = Mock(spec=Session)
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock(side_effect=lambda p: setattr(p, "id", 1))
        return db

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def mock_preferences(self):
        """Create mock user preferences with notifications enabled."""
        prefs = Mock(spec=UserPreferences)
        prefs.email_notifications = True
        prefs.price_drop_alerts = True
        return prefs

    @pytest.fixture
    def mock_background_tasks(self):
        """Create a mock background tasks object."""
        return Mock(spec=BackgroundTasks)

    @pytest.mark.asyncio
    @patch("app.api.endpoints.products.scraper.scrape_product")
    @patch("app.api.endpoints.products.price_history_service.record_price")
    @patch("app.api.endpoints.products.email_service.send_price_alert")
    async def test_create_product_sends_alert_when_price_below_target(
        self,
        mock_send_alert,
        mock_record_price,
        mock_scrape,
        mock_db,
        mock_user,
        mock_preferences,
        mock_background_tasks,
    ):
        """Test that an alert is sent when product is created with price below target."""
        # Setup: scraped price (50) is below target price (100)
        mock_scrape.return_value = Mock(name="Test Product", price=50.0, image="http://example.com/img.jpg")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_preferences

        product_data = ProductCreate(url="http://example.com/product", target_price=100.0)

        from app.api.endpoints.products import create_product

        result = create_product(product_data, mock_background_tasks, mock_user, mock_db)

        # Verify alert was scheduled
        mock_background_tasks.add_task.assert_called_once()
        call_args = mock_background_tasks.add_task.call_args
        assert call_args[0][0] == mock_send_alert  # First arg is the function
        assert call_args[0][1] == "test@example.com"  # to_email
        assert call_args[0][3] == 50.0  # new_price
        assert call_args[1]["user_preferences"] == mock_preferences

    @pytest.mark.asyncio
    @patch("app.api.endpoints.products.scraper.scrape_product")
    @patch("app.api.endpoints.products.price_history_service.record_price")
    async def test_create_product_no_alert_when_price_above_target(
        self, mock_record_price, mock_scrape, mock_db, mock_user, mock_background_tasks
    ):
        """Test that no alert is sent when product price is above target."""
        # Setup: scraped price (150) is above target price (100)
        mock_scrape.return_value = Mock(name="Test Product", price=150.0, image="http://example.com/img.jpg")

        product_data = ProductCreate(url="http://example.com/product", target_price=100.0)

        from app.api.endpoints.products import create_product

        result = create_product(product_data, mock_background_tasks, mock_user, mock_db)

        # Verify no alert was scheduled
        mock_background_tasks.add_task.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.api.endpoints.products.scraper.scrape_product")
    @patch("app.api.endpoints.products.price_history_service.record_price")
    @patch("app.api.endpoints.products.email_service.send_price_alert")
    async def test_create_product_sends_alert_when_price_equals_target(
        self,
        mock_send_alert,
        mock_record_price,
        mock_scrape,
        mock_db,
        mock_user,
        mock_preferences,
        mock_background_tasks,
    ):
        """Test that an alert is sent when product price equals target price."""
        # Setup: scraped price (100) equals target price (100)
        mock_scrape.return_value = Mock(name="Test Product", price=100.0, image="http://example.com/img.jpg")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_preferences

        product_data = ProductCreate(url="http://example.com/product", target_price=100.0)

        from app.api.endpoints.products import create_product

        result = create_product(product_data, mock_background_tasks, mock_user, mock_db)

        # Verify alert was scheduled
        mock_background_tasks.add_task.assert_called_once()


@pytest.mark.unit
class TestCheckProductPriceAlert:
    """Test suite for manual price check with alerts."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = Mock(spec=Session)
        db.commit = Mock()
        db.refresh = Mock()
        return db

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        return user

    @pytest.fixture
    def mock_product(self):
        """Create a mock product."""
        product = Mock(spec=Product)
        product.id = 1
        product.user_id = 1
        product.name = "Test Product"
        product.url = "http://example.com/product"
        product.current_price = 150.0
        product.target_price = 100.0
        return product

    @pytest.fixture
    def mock_preferences(self):
        """Create mock user preferences with notifications enabled."""
        prefs = Mock(spec=UserPreferences)
        prefs.email_notifications = True
        prefs.price_drop_alerts = True
        return prefs

    @pytest.fixture
    def mock_background_tasks(self):
        """Create a mock background tasks object."""
        return Mock(spec=BackgroundTasks)

    @pytest.mark.asyncio
    @patch("app.api.endpoints.products.scraper.scrape_product")
    @patch("app.api.endpoints.products.price_history_service.should_record_price")
    @patch("app.api.endpoints.products.price_history_service.record_price")
    @patch("app.api.endpoints.products.email_service.send_price_alert")
    async def test_check_price_sends_alert_when_crossing_target(
        self,
        mock_send_alert,
        mock_record_price,
        mock_should_record,
        mock_scrape,
        mock_db,
        mock_user,
        mock_product,
        mock_preferences,
        mock_background_tasks,
    ):
        """Test that alert is sent when price drops below target."""
        # Setup: price drops from 150 to 80 (below target of 100)
        mock_scrape.return_value = Mock(price=80.0)
        mock_should_record.return_value = True
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_product, mock_preferences]

        from app.api.endpoints.products import check_product_price

        result = check_product_price(1, mock_background_tasks, mock_user, mock_db)

        # Verify alert was scheduled
        mock_background_tasks.add_task.assert_called_once()
        call_args = mock_background_tasks.add_task.call_args
        assert call_args[0][3] == 80.0  # new_price
        assert call_args[0][4] == 150.0  # old_price

    @pytest.mark.asyncio
    @patch("app.api.endpoints.products.scraper.scrape_product")
    @patch("app.api.endpoints.products.price_history_service.should_record_price")
    @patch("app.api.endpoints.products.price_history_service.record_price")
    async def test_check_price_no_alert_when_already_below_target(
        self,
        mock_record_price,
        mock_should_record,
        mock_scrape,
        mock_db,
        mock_user,
        mock_product,
        mock_background_tasks,
    ):
        """Test that no alert is sent when price was already below target."""
        # Setup: price was already 80 (below 100), stays at 80
        mock_product.current_price = 80.0
        mock_scrape.return_value = Mock(price=75.0)
        mock_should_record.return_value = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_product

        from app.api.endpoints.products import check_product_price

        result = check_product_price(1, mock_background_tasks, mock_user, mock_db)

        # Verify no alert was scheduled (price was already below target)
        mock_background_tasks.add_task.assert_not_called()
