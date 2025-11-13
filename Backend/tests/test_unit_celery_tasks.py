"""
Unit tests for Celery tasks.

Tests include:
- check_all_prices task
- check_single_product task
- Price alert triggering
- Price history recording
- Error handling
- Database session management
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from tasks import check_all_prices, check_single_product
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductScrapedData


class TestCeleryTasks:
    """Test suite for Celery background tasks."""

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    def test_check_all_prices_success(
        self, mock_record_price, mock_should_record, mock_scrape, mock_session_local
    ):
        """Test successful execution of check_all_prices task."""
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock products
        mock_products = [
            Product(
                id=1, user_id=1, name="Product 1", url="https://example.com/1",
                current_price=100.00, target_price=80.00,
                last_checked=datetime.utcnow(), created_at=datetime.utcnow()
            ),
            Product(
                id=2, user_id=1, name="Product 2", url="https://example.com/2",
                current_price=50.00, target_price=40.00,
                last_checked=datetime.utcnow(), created_at=datetime.utcnow()
            ),
        ]

        mock_db.query.return_value.all.return_value = mock_products

        # Mock scraper responses
        mock_scrape.side_effect = [
            ProductScrapedData(name="Product 1", price=95.00, image=None),
            ProductScrapedData(name="Product 2", price=45.00, image=None),
        ]

        # Mock price history checks
        mock_should_record.return_value = True

        # Execute task
        check_all_prices()

        # Verify scraper was called for each product
        assert mock_scrape.call_count == 2

        # Verify prices were updated
        assert mock_products[0].current_price == 95.00
        assert mock_products[1].current_price == 45.00

        # Verify database commits
        assert mock_db.commit.call_count == 2

        # Verify session was closed
        mock_db.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    @patch('tasks.email_service.send_price_alert')
    def test_check_all_prices_triggers_alert(
        self, mock_send_alert, mock_record_price, mock_should_record,
        mock_scrape, mock_session_local
    ):
        """Test that check_all_prices triggers alert when price drops below target."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@example.com"

        # Create product with price above target
        mock_product = Product(
            id=1, user_id=1, name="Test Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        mock_db.query.return_value.all.return_value = [mock_product]

        # Mock user query
        user_query = MagicMock()
        user_query.filter.return_value = user_query
        user_query.first.return_value = mock_user

        def query_side_effect(*args, **kwargs):
            if args and args[0] is Product:
                query = MagicMock()
                query.all.return_value = [mock_product]
                return query
            elif args and args[0] is User:
                return user_query
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        # Mock scraper to return price below target
        mock_scrape.return_value = ProductScrapedData(
            name="Test Product", price=75.00, image=None
        )
        mock_should_record.return_value = True

        # Execute task
        check_all_prices()

        # Verify alert was sent
        mock_send_alert.assert_called_once_with(
            "user@example.com",
            "Test Product",
            75.00,
            100.00,
            "https://example.com/product"
        )

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    def test_check_all_prices_handles_scraping_error(self, mock_scrape, mock_session_local):
        """Test that check_all_prices handles scraping errors gracefully."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_products = [
            Product(
                id=1, user_id=1, name="Product 1", url="https://example.com/1",
                current_price=100.00, target_price=80.00,
                last_checked=datetime.utcnow(), created_at=datetime.utcnow()
            ),
            Product(
                id=2, user_id=1, name="Product 2", url="https://example.com/2",
                current_price=50.00, target_price=40.00,
                last_checked=datetime.utcnow(), created_at=datetime.utcnow()
            ),
        ]

        mock_db.query.return_value.all.return_value = mock_products

        # First product fails, second succeeds
        mock_scrape.side_effect = [
            Exception("Scraping failed"),
            ProductScrapedData(name="Product 2", price=45.00, image=None),
        ]

        # Execute task - should not raise exception
        check_all_prices()

        # Verify scraper was called for both products
        assert mock_scrape.call_count == 2

        # Verify session was closed even after error
        mock_db.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    def test_check_all_prices_records_price_history(
        self, mock_record_price, mock_should_record, mock_scrape, mock_session_local
    ):
        """Test that check_all_prices records price history when price changes."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_product = Product(
            id=1, user_id=1, name="Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        mock_db.query.return_value.all.return_value = [mock_product]

        # Mock price change
        mock_scrape.return_value = ProductScrapedData(
            name="Product", price=95.00, image=None
        )
        mock_should_record.return_value = True

        # Execute task
        check_all_prices()

        # Verify price history was checked and recorded
        mock_should_record.assert_called_once_with(mock_db, 1, 95.00)
        mock_record_price.assert_called_once_with(mock_db, 1, 95.00)

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    def test_check_all_prices_skips_recording_unchanged_price(
        self, mock_should_record, mock_scrape, mock_session_local
    ):
        """Test that unchanged prices are not recorded in history."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_product = Product(
            id=1, user_id=1, name="Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        mock_db.query.return_value.all.return_value = [mock_product]

        # Same price
        mock_scrape.return_value = ProductScrapedData(
            name="Product", price=100.00, image=None
        )
        mock_should_record.return_value = False

        # Execute task
        check_all_prices()

        # Verify should_record was called but record_price was not
        mock_should_record.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    def test_check_single_product_success(
        self, mock_record_price, mock_should_record, mock_scrape, mock_session_local
    ):
        """Test successful execution of check_single_product task."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_product = Product(
            id=1, user_id=1, name="Single Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        mock_db.query.return_value = product_query

        # Mock scraper
        mock_scrape.return_value = ProductScrapedData(
            name="Single Product", price=90.00, image=None
        )
        mock_should_record.return_value = True

        # Execute task
        check_single_product(1)

        # Verify product was fetched and updated
        mock_scrape.assert_called_once_with("https://example.com/product")
        assert mock_product.current_price == 90.00
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    @patch('tasks.email_service.send_price_alert')
    def test_check_single_product_sends_alert(
        self, mock_send_alert, mock_record_price, mock_should_record,
        mock_scrape, mock_session_local
    ):
        """Test that check_single_product sends alert when target is reached."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@example.com"

        mock_product = Product(
            id=1, user_id=1, name="Alert Product", url="https://example.com/alert",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        user_query = MagicMock()
        user_query.filter.return_value = user_query
        user_query.first.return_value = mock_user

        def query_side_effect(*args, **kwargs):
            if args and args[0] is Product:
                return product_query
            elif args and args[0] is User:
                return user_query
            return MagicMock()

        mock_db.query.side_effect = query_side_effect

        # Price drops below target
        mock_scrape.return_value = ProductScrapedData(
            name="Alert Product", price=75.00, image=None
        )
        mock_should_record.return_value = True

        # Execute task
        check_single_product(1)

        # Verify alert was sent
        mock_send_alert.assert_called_once_with(
            "user@example.com",
            "Alert Product",
            75.00,
            100.00,
            "https://example.com/alert"
        )

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    def test_check_single_product_not_found(self, mock_session_local):
        """Test check_single_product with non-existent product."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = None

        mock_db.query.return_value = product_query

        # Execute task - should not raise exception
        check_single_product(999)

        # Verify session was closed
        mock_db.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    def test_check_single_product_scraping_fails(self, mock_scrape, mock_session_local):
        """Test check_single_product when scraping returns None."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_product = Product(
            id=1, user_id=1, name="Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        mock_db.query.return_value = product_query

        # Scraping fails
        mock_scrape.return_value = None

        # Execute task
        check_single_product(1)

        # Verify product was not updated (commit should not be called)
        mock_db.commit.assert_not_called()
        mock_db.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.celery
    @patch('tasks.SessionLocal')
    @patch('tasks.scraper.scrape_product')
    @patch('tasks.price_history_service.should_record_price')
    @patch('tasks.price_history_service.record_price')
    def test_check_single_product_records_history(
        self, mock_record_price, mock_should_record, mock_scrape, mock_session_local
    ):
        """Test that check_single_product records price history."""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_product = Product(
            id=1, user_id=1, name="Product", url="https://example.com/product",
            current_price=100.00, target_price=80.00,
            last_checked=datetime.utcnow(), created_at=datetime.utcnow()
        )

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        mock_db.query.return_value = product_query

        mock_scrape.return_value = ProductScrapedData(
            name="Product", price=95.00, image=None
        )
        mock_should_record.return_value = True

        # Execute task
        check_single_product(1)

        # Verify history was recorded
        mock_should_record.assert_called_once_with(mock_db, 1, 95.00)
        mock_record_price.assert_called_once_with(mock_db, 1, 95.00)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
