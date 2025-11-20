"""
Unit tests for the PriceHistoryService.

Tests include:
- Recording prices
- Retrieving price history
- Calculating statistics
- Checking if price should be recorded
- Edge cases and error handling
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

from app.models.price_history import PriceHistory
from app.models.product import Product
from app.services.price_history import PriceHistoryService, price_history_service


class TestPriceHistoryService:
    """Test suite for PriceHistoryService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = PriceHistoryService()
        self.mock_db = MagicMock()

    @pytest.mark.unit
    def test_service_initialization(self):
        """Test that service initializes correctly."""
        assert self.service is not None
        assert isinstance(self.service, PriceHistoryService)

    @pytest.mark.unit
    def test_record_price_success(self):
        """Test successfully recording a price."""
        product_id = 1
        price = 99.99

        # Mock the database operations
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()

        result = self.service.record_price(self.mock_db, product_id, price)

        assert result is not None
        assert result.product_id == product_id
        assert result.price == price
        assert result.recorded_at is not None
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    @pytest.mark.unit
    def test_record_price_with_different_values(self):
        """Test recording multiple different prices."""
        test_cases = [
            (1, 50.00),
            (2, 199.99),
            (3, 1299.99),
        ]

        for product_id, price in test_cases:
            mock_db = MagicMock()
            result = self.service.record_price(mock_db, product_id, price)

            assert result.product_id == product_id
            assert result.price == price

    @pytest.mark.unit
    def test_get_product_history_no_limit(self):
        """Test retrieving product history without limit."""
        product_id = 1

        # Create mock price history records
        mock_records = [
            PriceHistory(id=3, product_id=1, price=90.00, recorded_at=datetime.utcnow()),
            PriceHistory(id=2, product_id=1, price=95.00, recorded_at=datetime.utcnow() - timedelta(days=1)),
            PriceHistory(id=1, product_id=1, price=100.00, recorded_at=datetime.utcnow() - timedelta(days=2)),
        ]

        # Mock query chain
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_records

        self.mock_db.query.return_value = mock_query

        result = self.service.get_product_history(self.mock_db, product_id)

        assert len(result) == 3
        assert result[0].price == 90.00  # Most recent first
        assert result[1].price == 95.00
        assert result[2].price == 100.00

    @pytest.mark.unit
    def test_get_product_history_with_limit(self):
        """Test retrieving product history with limit."""
        product_id = 1
        limit = 2

        mock_records = [
            PriceHistory(id=3, product_id=1, price=90.00, recorded_at=datetime.utcnow()),
            PriceHistory(id=2, product_id=1, price=95.00, recorded_at=datetime.utcnow() - timedelta(days=1)),
        ]

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_records

        self.mock_db.query.return_value = mock_query

        result = self.service.get_product_history(self.mock_db, product_id, limit=limit)

        assert len(result) == 2
        mock_query.limit.assert_called_once_with(limit)

    @pytest.mark.unit
    def test_get_product_history_empty(self):
        """Test retrieving history for product with no records."""
        product_id = 999

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        self.mock_db.query.return_value = mock_query

        result = self.service.get_product_history(self.mock_db, product_id)

        assert result == []

    @pytest.mark.unit
    def test_get_price_statistics_with_history(self):
        """Test calculating price statistics with existing history."""
        product_id = 1

        # Mock product
        mock_product = Product(
            id=1,
            user_id=1,
            name="Test Product",
            url="https://example.com",
            current_price=90.00,
            target_price=80.00,
            last_checked=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        # Mock statistics query result
        mock_stats = Mock()
        mock_stats.lowest = 85.00
        mock_stats.highest = 120.00
        mock_stats.average = 102.50
        mock_stats.total = 5

        # Mock first price for change calculation
        mock_first_price = (100.00,)

        # Set up query mocks
        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        stats_query = MagicMock()
        stats_query.filter.return_value = stats_query
        stats_query.first.return_value = mock_stats

        first_price_query = MagicMock()
        first_price_query.filter.return_value = first_price_query
        first_price_query.order_by.return_value = first_price_query
        first_price_query.first.return_value = mock_first_price

        # Configure mock_db to return different queries based on the model
        def query_side_effect(*args, **kwargs):
            # First argument is the model or expression
            if args and args[0] is Product:
                return product_query
            elif args and len(args) > 1:
                # Multiple arguments = aggregation query
                return stats_query
            else:
                return first_price_query

        self.mock_db.query.side_effect = query_side_effect

        result = self.service.get_price_statistics(self.mock_db, product_id)

        assert result is not None
        assert result["current_price"] == 90.00
        assert result["lowest_price"] == 85.00
        assert result["highest_price"] == 120.00
        assert result["average_price"] == 102.50
        assert result["total_records"] == 5
        # Price dropped from 100 to 90: -10%
        assert result["price_change_percentage"] == -10.0

    @pytest.mark.unit
    def test_get_price_statistics_no_history(self):
        """Test statistics when no price history exists."""
        product_id = 1

        mock_product = Product(
            id=1,
            user_id=1,
            name="New Product",
            url="https://example.com",
            current_price=99.99,
            target_price=80.00,
            last_checked=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        mock_stats = Mock()
        mock_stats.total = 0

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        stats_query = MagicMock()
        stats_query.filter.return_value = stats_query
        stats_query.first.return_value = mock_stats

        def query_side_effect(*args, **kwargs):
            if args and args[0] is Product:
                return product_query
            else:
                return stats_query

        self.mock_db.query.side_effect = query_side_effect

        result = self.service.get_price_statistics(self.mock_db, product_id)

        assert result is not None
        assert result["current_price"] == 99.99
        assert result["lowest_price"] == 99.99
        assert result["highest_price"] == 99.99
        assert result["average_price"] == 99.99
        assert result["price_change_percentage"] == 0.0
        assert result["total_records"] == 0

    @pytest.mark.unit
    def test_get_price_statistics_product_not_found(self):
        """Test statistics when product doesn't exist."""
        product_id = 999

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        self.mock_db.query.return_value = mock_query

        result = self.service.get_price_statistics(self.mock_db, product_id)

        assert result is None

    @pytest.mark.unit
    def test_should_record_price_no_history(self):
        """Test should_record_price when no history exists."""
        product_id = 1
        new_price = 99.99

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None

        self.mock_db.query.return_value = mock_query

        result = self.service.should_record_price(self.mock_db, product_id, new_price)

        assert result is True

    @pytest.mark.unit
    def test_should_record_price_changed(self):
        """Test should_record_price when price has changed."""
        product_id = 1
        new_price = 89.99

        mock_last_record = PriceHistory(id=1, product_id=1, price=99.99, recorded_at=datetime.utcnow())

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_last_record

        self.mock_db.query.return_value = mock_query

        result = self.service.should_record_price(self.mock_db, product_id, new_price)

        assert result is True

    @pytest.mark.unit
    def test_should_record_price_unchanged(self):
        """Test should_record_price when price hasn't changed."""
        product_id = 1
        new_price = 99.99

        mock_last_record = PriceHistory(id=1, product_id=1, price=99.99, recorded_at=datetime.utcnow())

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_last_record

        self.mock_db.query.return_value = mock_query

        result = self.service.should_record_price(self.mock_db, product_id, new_price)

        assert result is False

    @pytest.mark.unit
    def test_price_change_percentage_calculation_increase(self):
        """Test price change percentage when price increases."""
        # If first price was 100 and current is 120, change is +20%
        product_id = 1

        mock_product = Product(
            id=1,
            user_id=1,
            name="Test",
            url="https://example.com",
            current_price=120.00,
            target_price=80.00,
            last_checked=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        mock_stats = Mock()
        mock_stats.lowest = 100.00
        mock_stats.highest = 120.00
        mock_stats.average = 110.00
        mock_stats.total = 3

        mock_first_price = (100.00,)

        product_query = MagicMock()
        product_query.filter.return_value = product_query
        product_query.first.return_value = mock_product

        stats_query = MagicMock()
        stats_query.filter.return_value = stats_query
        stats_query.first.return_value = mock_stats

        first_price_query = MagicMock()
        first_price_query.filter.return_value = first_price_query
        first_price_query.order_by.return_value = first_price_query
        first_price_query.first.return_value = mock_first_price

        def query_side_effect(*args, **kwargs):
            if args and args[0] is Product:
                return product_query
            elif args and len(args) > 1:
                # Multiple arguments = aggregation query
                return stats_query
            else:
                return first_price_query

        self.mock_db.query.side_effect = query_side_effect

        result = self.service.get_price_statistics(self.mock_db, product_id)

        assert result["price_change_percentage"] == 20.0

    @pytest.mark.unit
    def test_singleton_price_history_service_instance(self):
        """Test that price_history_service singleton is correctly instantiated."""
        assert price_history_service is not None
        assert isinstance(price_history_service, PriceHistoryService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
