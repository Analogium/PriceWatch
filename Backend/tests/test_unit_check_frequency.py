"""
Unit tests for check_frequency functionality.
Tests the product check frequency feature (6h, 12h, 24h).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product


@pytest.mark.unit
class TestCheckFrequencyValidation:
    """Test validation of check_frequency field in Pydantic schemas."""

    def test_product_create_default_frequency(self):
        """Test that ProductCreate has default check_frequency of 24 hours."""
        product = ProductCreate(
            url="https://amazon.fr/test",
            target_price=100.0
        )
        assert product.check_frequency == 24

    def test_product_create_valid_frequency_6h(self):
        """Test that ProductCreate accepts 6 hours as valid frequency."""
        product = ProductCreate(
            url="https://amazon.fr/test",
            target_price=100.0,
            check_frequency=6
        )
        assert product.check_frequency == 6

    def test_product_create_valid_frequency_12h(self):
        """Test that ProductCreate accepts 12 hours as valid frequency."""
        product = ProductCreate(
            url="https://amazon.fr/test",
            target_price=100.0,
            check_frequency=12
        )
        assert product.check_frequency == 12

    def test_product_create_valid_frequency_24h(self):
        """Test that ProductCreate accepts 24 hours as valid frequency."""
        product = ProductCreate(
            url="https://amazon.fr/test",
            target_price=100.0,
            check_frequency=24
        )
        assert product.check_frequency == 24

    def test_product_create_invalid_frequency(self):
        """Test that ProductCreate rejects invalid check_frequency values."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                url="https://amazon.fr/test",
                target_price=100.0,
                check_frequency=48  # Invalid: not in [6, 12, 24]
            )

        assert "check_frequency must be 6, 12, or 24 hours" in str(exc_info.value)

    def test_product_update_valid_frequency(self):
        """Test that ProductUpdate accepts valid check_frequency."""
        product_update = ProductUpdate(check_frequency=12)
        assert product_update.check_frequency == 12

    def test_product_update_invalid_frequency(self):
        """Test that ProductUpdate rejects invalid check_frequency."""
        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(check_frequency=3)

        assert "check_frequency must be 6, 12, or 24 hours" in str(exc_info.value)

    def test_product_update_none_frequency(self):
        """Test that ProductUpdate accepts None for check_frequency."""
        product_update = ProductUpdate(check_frequency=None)
        assert product_update.check_frequency is None


@pytest.mark.unit
@pytest.mark.celery
class TestCheckPricesByFrequency:
    """Test the check_prices_by_frequency Celery task."""

    @patch('tasks.SessionLocal')
    @patch('tasks.scraper')
    @patch('tasks.price_history_service')
    @patch('tasks.logger')
    def test_check_prices_by_frequency_filters_by_frequency(
        self, mock_logger, mock_price_service, mock_scraper, mock_session_local
    ):
        """Test that check_prices_by_frequency only checks products with the specified frequency."""
        from tasks import check_prices_by_frequency

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Mock query to return empty list
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        # Call the task
        check_prices_by_frequency(6)

        # Verify that query filtered by check_frequency
        assert mock_db.query.called
        assert mock_query.filter.called

    @patch('tasks.SessionLocal')
    @patch('tasks.scrape_products_parallel')
    @patch('tasks.price_history_service')
    @patch('tasks.email_service')
    @patch('tasks.logger')
    @patch('tasks.settings')
    def test_check_prices_by_frequency_respects_last_checked(
        self, mock_settings, mock_logger, mock_email, mock_price_service, mock_scrape_parallel, mock_session_local
    ):
        """Test that task only checks products not checked recently."""
        from tasks import check_prices_by_frequency

        # Configure settings
        mock_settings.SCRAPING_BATCH_SIZE = 10

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock products
        recent_product = Mock(spec=Product)
        recent_product.id = 1
        recent_product.check_frequency = 6
        recent_product.last_checked = datetime.utcnow() - timedelta(hours=3)

        old_product = Mock(spec=Product)
        old_product.id = 2
        old_product.check_frequency = 6
        old_product.last_checked = datetime.utcnow() - timedelta(hours=7)
        old_product.name = "Test Product"
        old_product.url = "https://amazon.fr/test"
        old_product.current_price = 100.0
        old_product.target_price = 90.0
        old_product.is_available = True

        # Mock query to return only old product (DB would filter recent ones)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [old_product]

        # Mock parallel scraping
        mock_scrape_parallel.return_value = [(old_product, 90.0, None)]

        # Mock price history service
        mock_price_service.should_record_price.return_value = True

        # Call the task
        check_prices_by_frequency(6)

        # Verify parallel scraping was called with the old product
        mock_scrape_parallel.assert_called_once()
        batch_products = mock_scrape_parallel.call_args[0][0]
        assert len(batch_products) == 1
        assert batch_products[0] is old_product

    @patch('tasks.SessionLocal')
    @patch('tasks.scraper')
    @patch('tasks.price_history_service')
    @patch('tasks.email_service')
    @patch('tasks.logger')
    def test_check_prices_by_frequency_sends_alert(
        self, mock_logger, mock_email, mock_price_service, mock_scraper, mock_session_local
    ):
        """Test that task sends alert when price drops below target."""
        from tasks import check_prices_by_frequency
        from app.models.user import User
        from app.models.user_preferences import UserPreferences

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock product
        mock_product = Mock(spec=Product)
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.url = "https://amazon.fr/test"
        mock_product.current_price = 150.0
        mock_product.target_price = 100.0
        mock_product.user_id = 1
        mock_product.is_available = True

        # Create mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"

        # Create mock preferences
        mock_preferences = Mock(spec=UserPreferences)
        mock_preferences.email_notifications = True

        # Mock query for products
        mock_product_query = MagicMock()
        mock_db.query.return_value = mock_product_query
        mock_product_query.filter.return_value = mock_product_query

        # First query returns products, subsequent queries return user and preferences
        def query_side_effect(model):
            if model is Product:
                q = MagicMock()
                q.filter.return_value = q
                q.all.return_value = [mock_product]
                return q
            elif model is User:
                q = MagicMock()
                q.filter.return_value = q
                q.first.return_value = mock_user
                return q
            elif model is UserPreferences:
                q = MagicMock()
                q.filter.return_value = q
                q.first.return_value = mock_preferences
                return q
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        # Mock scraper with price below target
        mock_scraped = Mock()
        mock_scraped.price = 90.0
        mock_scraper.scrape_product.return_value = mock_scraped

        # Mock price history service
        mock_price_service.should_record_price.return_value = True

        # Call the task
        check_prices_by_frequency(24)

        # Verify email was sent
        mock_email.send_price_alert.assert_called_once_with(
            "test@example.com",
            "Test Product",
            90.0,
            150.0,
            "https://amazon.fr/test",
            user_preferences=mock_preferences
        )


@pytest.mark.unit
class TestProductModelFrequency:
    """Test the Product model with check_frequency field."""

    def test_product_has_check_frequency_field(self):
        """Test that Product model has check_frequency column."""
        from app.models.product import Product

        # Check that the column exists
        assert hasattr(Product, 'check_frequency')

        # Check that it's a SQLAlchemy Column
        from sqlalchemy.orm import InstrumentedAttribute
        assert isinstance(Product.check_frequency, InstrumentedAttribute)

    def test_product_default_frequency(self):
        """Test that Product has default check_frequency of 24."""
        from app.models.product import Product

        # Get the column default
        column = Product.__table__.columns['check_frequency']
        assert column.default.arg == 24
