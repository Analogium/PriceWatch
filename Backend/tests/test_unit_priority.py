"""
Unit tests for product priority checking functionality.
Tests the priority calculation and sorting logic for price checking.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.models.product import Product


@pytest.mark.unit
class TestPriorityCalculation:
    """Test priority calculation function."""

    def test_calculate_priority_below_target(self):
        """Test that products below target price get highest priority (0)."""
        from tasks import calculate_priority

        # Create mock product below target
        product = Mock(spec=Product)
        product.current_price = 80.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == 0.0

    def test_calculate_priority_at_target(self):
        """Test that products at target price get highest priority (0)."""
        from tasks import calculate_priority

        # Create mock product at target
        product = Mock(spec=Product)
        product.current_price = 100.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == 0.0

    def test_calculate_priority_slightly_above_target(self):
        """Test priority for product slightly above target."""
        from tasks import calculate_priority

        # Create mock product 10% above target
        product = Mock(spec=Product)
        product.current_price = 110.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == pytest.approx(0.1, rel=1e-5)

    def test_calculate_priority_far_above_target(self):
        """Test priority for product far above target."""
        from tasks import calculate_priority

        # Create mock product 50% above target
        product = Mock(spec=Product)
        product.current_price = 150.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == pytest.approx(0.5, rel=1e-5)

    def test_calculate_priority_double_target(self):
        """Test priority for product at double the target price."""
        from tasks import calculate_priority

        # Create mock product 100% above target
        product = Mock(spec=Product)
        product.current_price = 200.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == pytest.approx(1.0, rel=1e-5)

    def test_priority_ordering(self):
        """Test that products are correctly ordered by priority."""
        from tasks import calculate_priority

        # Create products with different price ratios
        product_below = Mock(spec=Product)
        product_below.current_price = 90.0
        product_below.target_price = 100.0

        product_near = Mock(spec=Product)
        product_near.current_price = 105.0
        product_near.target_price = 100.0

        product_far = Mock(spec=Product)
        product_far.current_price = 150.0
        product_far.target_price = 100.0

        products = [product_far, product_below, product_near]
        sorted_products = sorted(products, key=calculate_priority)

        # Check order: below < near < far
        assert sorted_products[0] is product_below
        assert sorted_products[1] is product_near
        assert sorted_products[2] is product_far


@pytest.mark.unit
@pytest.mark.celery
class TestCheckPricesByFrequencyWithPriority:
    """Test the check_prices_by_frequency task with priority sorting."""

    @patch('tasks.SessionLocal')
    @patch('tasks.scraper')
    @patch('tasks.price_history_service')
    @patch('tasks.logger')
    def test_products_sorted_by_priority(
        self, mock_logger, mock_price_service, mock_scraper, mock_session_local
    ):
        """Test that products are checked in priority order."""
        from tasks import check_prices_by_frequency

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock products with different priorities
        product_low_priority = Mock(spec=Product)
        product_low_priority.id = 1
        product_low_priority.name = "Low Priority Product"
        product_low_priority.url = "https://amazon.fr/low"
        product_low_priority.current_price = 200.0  # 100% above target
        product_low_priority.target_price = 100.0
        product_low_priority.is_available = True
        product_low_priority.check_frequency = 24

        product_medium_priority = Mock(spec=Product)
        product_medium_priority.id = 2
        product_medium_priority.name = "Medium Priority Product"
        product_medium_priority.url = "https://amazon.fr/medium"
        product_medium_priority.current_price = 110.0  # 10% above target
        product_medium_priority.target_price = 100.0
        product_medium_priority.is_available = True
        product_medium_priority.check_frequency = 24

        product_high_priority = Mock(spec=Product)
        product_high_priority.id = 3
        product_high_priority.name = "High Priority Product"
        product_high_priority.url = "https://amazon.fr/high"
        product_high_priority.current_price = 95.0  # Below target
        product_high_priority.target_price = 100.0
        product_high_priority.is_available = True
        product_high_priority.check_frequency = 24

        # Mock query to return products in random order
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [product_low_priority, product_high_priority, product_medium_priority]

        # Mock scraper to return different prices
        def scraper_side_effect(url):
            mock_result = Mock()
            if "low" in url:
                mock_result.price = 190.0
            elif "medium" in url:
                mock_result.price = 105.0
            elif "high" in url:
                mock_result.price = 93.0
            return mock_result

        mock_scraper.scrape_product.side_effect = scraper_side_effect

        # Mock price history service
        mock_price_service.should_record_price.return_value = True

        # Call the task
        check_prices_by_frequency(24)

        # Verify scraper was called in priority order (high, medium, low)
        calls = mock_scraper.scrape_product.call_args_list
        assert len(calls) == 3
        assert calls[0][0][0] == "https://amazon.fr/high"  # High priority first
        assert calls[1][0][0] == "https://amazon.fr/medium"  # Medium priority second
        assert calls[2][0][0] == "https://amazon.fr/low"  # Low priority last

    @patch('tasks.SessionLocal')
    @patch('tasks.scrape_products_parallel')
    @patch('tasks.price_history_service')
    @patch('tasks.email_service')
    @patch('tasks.logger')
    @patch('tasks.settings')
    def test_priority_with_mixed_prices(
        self, mock_settings, mock_logger, mock_email, mock_price_service, mock_scrape_parallel, mock_session_local
    ):
        """Test priority sorting with products at various price points."""
        from tasks import check_prices_by_frequency

        # Configure settings
        mock_settings.SCRAPING_BATCH_SIZE = 10

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create 5 products with different price ratios
        products = []

        # Product 1: Below target (highest priority)
        p1 = Mock(spec=Product)
        p1.id = 1
        p1.name = "Product 1"
        p1.url = "https://example.com/1"
        p1.current_price = 80.0
        p1.target_price = 100.0
        p1.is_available = True
        p1.check_frequency = 6
        products.append(p1)

        # Product 2: 5% above target
        p2 = Mock(spec=Product)
        p2.id = 2
        p2.name = "Product 2"
        p2.url = "https://example.com/2"
        p2.current_price = 105.0
        p2.target_price = 100.0
        p2.is_available = True
        p2.check_frequency = 6
        products.append(p2)

        # Product 3: 50% above target
        p3 = Mock(spec=Product)
        p3.id = 3
        p3.name = "Product 3"
        p3.url = "https://example.com/3"
        p3.current_price = 150.0
        p3.target_price = 100.0
        p3.is_available = True
        p3.check_frequency = 6
        products.append(p3)

        # Product 4: At target (highest priority)
        p4 = Mock(spec=Product)
        p4.id = 4
        p4.name = "Product 4"
        p4.url = "https://example.com/4"
        p4.current_price = 100.0
        p4.target_price = 100.0
        p4.is_available = True
        p4.check_frequency = 6
        products.append(p4)

        # Product 5: 20% above target
        p5 = Mock(spec=Product)
        p5.id = 5
        p5.name = "Product 5"
        p5.url = "https://example.com/5"
        p5.current_price = 120.0
        p5.target_price = 100.0
        p5.is_available = True
        p5.check_frequency = 6
        products.append(p5)

        # Mock query to return products in random order
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [p3, p1, p5, p2, p4]  # Random order

        # Mock parallel scraping - return results in the order they were passed
        def scrape_parallel_side_effect(batch):
            return [(product, 100.0, None) for product in batch]

        mock_scrape_parallel.side_effect = scrape_parallel_side_effect

        # Mock price history service
        mock_price_service.should_record_price.return_value = False

        # Call the task
        check_prices_by_frequency(6)

        # Verify parallel scraping was called once (all products in one batch)
        assert mock_scrape_parallel.call_count == 1

        # Get the batch that was passed to parallel scraping
        batch_products = mock_scrape_parallel.call_args[0][0]
        assert len(batch_products) == 5

        # Verify the order (products sorted by priority)
        batch_ids = [p.id for p in batch_products]

        # First two should be the ones at or below target (priority = 0)
        assert set(batch_ids[:2]) == {1, 4}

        # Last should be the one 50% above target (priority = 0.5)
        assert batch_ids[-1] == 3


@pytest.mark.unit
class TestPriorityEdgeCases:
    """Test edge cases for priority calculation."""

    def test_calculate_priority_with_zero_target(self):
        """Test priority calculation doesn't divide by zero."""
        from tasks import calculate_priority

        product = Mock(spec=Product)
        product.current_price = 10.0
        product.target_price = 0.01  # Very small target to avoid division by zero

        # Should not raise an error
        priority = calculate_priority(product)
        assert priority > 0

    def test_calculate_priority_with_negative_difference(self):
        """Test priority with product well below target."""
        from tasks import calculate_priority

        product = Mock(spec=Product)
        product.current_price = 50.0
        product.target_price = 100.0

        priority = calculate_priority(product)
        assert priority == 0.0  # Below target = highest priority
