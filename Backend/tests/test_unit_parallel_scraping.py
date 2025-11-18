"""
Unit tests for parallel scraping functionality.
Tests the concurrent scraping of multiple products.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.models.product import Product
from app.services.scraper import ProductUnavailableError


@pytest.mark.unit
class TestScrapeSingleProductSafe:
    """Test the scrape_single_product_safe function."""

    @patch('tasks.scraper')
    def test_scrape_single_product_safe_success(self, mock_scraper):
        """Test successful scraping of a single product."""
        from tasks import scrape_single_product_safe

        # Create mock product
        product = Mock(spec=Product)
        product.id = 1
        product.url = "https://amazon.fr/test"

        # Mock scraper
        mock_scraped = Mock()
        mock_scraped.price = 99.99
        mock_scraper.scrape_product.return_value = mock_scraped

        # Call function
        result_product, new_price, exception = scrape_single_product_safe(product)

        # Verify results
        assert result_product is product
        assert new_price == 99.99
        assert exception is None
        mock_scraper.scrape_product.assert_called_once_with(product.url)

    @patch('tasks.scraper')
    def test_scrape_single_product_safe_unavailable(self, mock_scraper):
        """Test scraping when product is unavailable."""
        from tasks import scrape_single_product_safe

        # Create mock product
        product = Mock(spec=Product)
        product.id = 1
        product.url = "https://amazon.fr/test"

        # Mock scraper to raise ProductUnavailableError
        mock_scraper.scrape_product.side_effect = ProductUnavailableError("Out of stock")

        # Call function
        result_product, new_price, exception = scrape_single_product_safe(product)

        # Verify results
        assert result_product is product
        assert new_price is None
        assert isinstance(exception, ProductUnavailableError)
        assert str(exception) == "Out of stock"

    @patch('tasks.scraper')
    def test_scrape_single_product_safe_error(self, mock_scraper):
        """Test scraping with generic error."""
        from tasks import scrape_single_product_safe

        # Create mock product
        product = Mock(spec=Product)
        product.id = 1
        product.url = "https://amazon.fr/test"

        # Mock scraper to raise exception
        mock_scraper.scrape_product.side_effect = Exception("Network error")

        # Call function
        result_product, new_price, exception = scrape_single_product_safe(product)

        # Verify results
        assert result_product is product
        assert new_price is None
        assert isinstance(exception, Exception)
        assert str(exception) == "Network error"

    @patch('tasks.scraper')
    def test_scrape_single_product_safe_no_data(self, mock_scraper):
        """Test scraping when no data is returned."""
        from tasks import scrape_single_product_safe

        # Create mock product
        product = Mock(spec=Product)
        product.id = 1
        product.url = "https://amazon.fr/test"

        # Mock scraper to return None
        mock_scraper.scrape_product.return_value = None

        # Call function
        result_product, new_price, exception = scrape_single_product_safe(product)

        # Verify results
        assert result_product is product
        assert new_price is None
        assert isinstance(exception, Exception)
        assert "No data returned" in str(exception)


@pytest.mark.unit
class TestScrapeProductsParallel:
    """Test the scrape_products_parallel function."""

    @patch('tasks.scrape_single_product_safe')
    def test_scrape_products_parallel_success(self, mock_scrape_safe):
        """Test parallel scraping of multiple products."""
        from tasks import scrape_products_parallel

        # Create mock products
        products = []
        for i in range(5):
            product = Mock(spec=Product)
            product.id = i + 1
            product.url = f"https://amazon.fr/product{i + 1}"
            products.append(product)

        # Mock scrape_single_product_safe to return success
        def scrape_side_effect(product):
            return (product, 100.0 + product.id, None)

        mock_scrape_safe.side_effect = scrape_side_effect

        # Call function
        results = scrape_products_parallel(products, max_workers=3)

        # Verify results
        assert len(results) == 5
        assert mock_scrape_safe.call_count == 5

        # Check that all products were scraped
        scraped_ids = {result[0].id for result in results}
        assert scraped_ids == {1, 2, 3, 4, 5}

    @patch('tasks.scrape_single_product_safe')
    def test_scrape_products_parallel_mixed_results(self, mock_scrape_safe):
        """Test parallel scraping with mixed success/failure."""
        from tasks import scrape_products_parallel

        # Create mock products
        products = []
        for i in range(3):
            product = Mock(spec=Product)
            product.id = i + 1
            product.url = f"https://amazon.fr/product{i + 1}"
            products.append(product)

        # Mock scrape_single_product_safe with mixed results
        def scrape_side_effect(product):
            if product.id == 1:
                return (product, 100.0, None)  # Success
            elif product.id == 2:
                return (product, None, ProductUnavailableError("Out of stock"))  # Unavailable
            else:
                return (product, None, Exception("Network error"))  # Error

        mock_scrape_safe.side_effect = scrape_side_effect

        # Call function
        results = scrape_products_parallel(products, max_workers=3)

        # Verify results
        assert len(results) == 3

        # Find each result
        success_result = next(r for r in results if r[0].id == 1)
        unavailable_result = next(r for r in results if r[0].id == 2)
        error_result = next(r for r in results if r[0].id == 3)

        assert success_result[1] == 100.0
        assert success_result[2] is None

        assert unavailable_result[1] is None
        assert isinstance(unavailable_result[2], ProductUnavailableError)

        assert error_result[1] is None
        assert isinstance(error_result[2], Exception)

    @patch('tasks.scrape_single_product_safe')
    def test_scrape_products_parallel_empty_list(self, mock_scrape_safe):
        """Test parallel scraping with empty product list."""
        from tasks import scrape_products_parallel

        # Call function with empty list
        results = scrape_products_parallel([])

        # Verify results
        assert len(results) == 0
        assert mock_scrape_safe.call_count == 0

    @patch('tasks.scrape_single_product_safe')
    @patch('tasks.settings')
    def test_scrape_products_parallel_uses_config(self, mock_settings, mock_scrape_safe):
        """Test that parallel scraping uses configured max_workers."""
        from tasks import scrape_products_parallel

        # Set mock settings
        mock_settings.MAX_PARALLEL_SCRAPERS = 3

        # Create mock products
        products = [Mock(spec=Product, id=i, url=f"https://test.com/{i}") for i in range(5)]

        # Mock scrape_single_product_safe
        mock_scrape_safe.side_effect = lambda p: (p, 100.0, None)

        # Call function without specifying max_workers (should use settings)
        results = scrape_products_parallel(products, max_workers=None)

        # Verify all products were scraped
        assert len(results) == 5


@pytest.mark.unit
@pytest.mark.celery
class TestCheckPricesByFrequencyWithParallel:
    """Test the check_prices_by_frequency task with parallel scraping."""

    @patch('tasks.SessionLocal')
    @patch('tasks.scrape_products_parallel')
    @patch('tasks.price_history_service')
    @patch('tasks.logger')
    @patch('tasks.settings')
    def test_check_prices_by_frequency_uses_parallel_scraping(
        self, mock_settings, mock_logger, mock_price_service, mock_scrape_parallel, mock_session_local
    ):
        """Test that the task uses parallel scraping."""
        from tasks import check_prices_by_frequency

        # Configure settings
        mock_settings.SCRAPING_BATCH_SIZE = 2
        mock_settings.MAX_PARALLEL_SCRAPERS = 5

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock products
        products = []
        for i in range(3):
            product = Mock(spec=Product)
            product.id = i + 1
            product.name = f"Product {i + 1}"
            product.url = f"https://test.com/{i + 1}"
            product.current_price = 100.0
            product.target_price = 90.0
            product.is_available = True
            product.check_frequency = 24
            products.append(product)

        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = products

        # Mock parallel scraping results
        def scrape_parallel_side_effect(batch):
            return [(product, 95.0, None) for product in batch]

        mock_scrape_parallel.side_effect = scrape_parallel_side_effect

        # Mock price history service
        mock_price_service.should_record_price.return_value = True

        # Call the task
        check_prices_by_frequency(24)

        # Verify scrape_products_parallel was called
        # With batch_size=2 and 3 products, should be called twice (batch of 2, then batch of 1)
        assert mock_scrape_parallel.call_count == 2

        # Verify batch sizes
        first_call_batch = mock_scrape_parallel.call_args_list[0][0][0]
        second_call_batch = mock_scrape_parallel.call_args_list[1][0][0]

        assert len(first_call_batch) == 2
        assert len(second_call_batch) == 1

    @patch('tasks.SessionLocal')
    @patch('tasks.scrape_products_parallel')
    @patch('tasks.price_history_service')
    @patch('tasks.logger')
    @patch('tasks.settings')
    def test_check_prices_by_frequency_handles_parallel_errors(
        self, mock_settings, mock_logger, mock_price_service, mock_scrape_parallel, mock_session_local
    ):
        """Test that the task correctly handles errors from parallel scraping."""
        from tasks import check_prices_by_frequency

        # Configure settings
        mock_settings.SCRAPING_BATCH_SIZE = 10

        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create mock products
        product1 = Mock(spec=Product, id=1, name="Product 1", url="https://test1.com",
                       current_price=100.0, target_price=90.0, is_available=True, check_frequency=24)
        product2 = Mock(spec=Product, id=2, name="Product 2", url="https://test2.com",
                       current_price=100.0, target_price=90.0, is_available=True, check_frequency=24)
        product3 = Mock(spec=Product, id=3, name="Product 3", url="https://test3.com",
                       current_price=100.0, target_price=90.0, is_available=True, check_frequency=24)

        products = [product1, product2, product3]

        # Mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = products

        # Mock parallel scraping with mixed results
        mock_scrape_parallel.return_value = [
            (product1, 95.0, None),  # Success
            (product2, None, ProductUnavailableError("Out of stock")),  # Unavailable
            (product3, None, Exception("Network error")),  # Error
        ]

        # Mock price history service
        mock_price_service.should_record_price.return_value = True

        # Call the task
        check_prices_by_frequency(24)

        # Verify database commits
        assert mock_db.commit.called

        # Verify product1 was updated
        assert product1.current_price == 95.0

        # Verify product2 was marked unavailable
        assert product2.is_available is False
        assert product2.unavailable_since is not None


@pytest.mark.unit
class TestParallelScrapingPerformance:
    """Test performance characteristics of parallel scraping."""

    @patch('tasks.scrape_single_product_safe')
    def test_parallel_scraping_faster_than_sequential(self, mock_scrape_safe):
        """Test that parallel scraping completes faster than sequential (conceptual test)."""
        from tasks import scrape_products_parallel
        import time

        # Create mock products
        products = [Mock(spec=Product, id=i, url=f"https://test.com/{i}") for i in range(10)]

        # Mock scraping with small delay
        def scrape_with_delay(product):
            time.sleep(0.01)  # 10ms delay per product
            return (product, 100.0, None)

        mock_scrape_safe.side_effect = scrape_with_delay

        # Measure parallel execution time
        start = time.time()
        results = scrape_products_parallel(products, max_workers=5)
        parallel_duration = time.time() - start

        # Verify all products were scraped
        assert len(results) == 10

        # With 10 products and 5 workers, should complete in ~2 batches (20ms)
        # Sequential would take 100ms (10 * 10ms)
        # Allow some overhead, but should be significantly faster
        assert parallel_duration < 0.05  # Should complete in under 50ms
