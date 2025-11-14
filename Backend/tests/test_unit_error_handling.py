"""
Unit tests for error handling features (logging, retry logic, unavailability detection).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from bs4 import BeautifulSoup
import requests
from datetime import datetime

from app.services.scraper import PriceScraper, ProductUnavailableError
from app.schemas.product import ProductScrapedData


@pytest.mark.unit
class TestRetryLogic:
    """Test retry logic in scraper."""

    @patch('app.services.scraper.requests.get')
    @patch('app.services.scraper.time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_get):
        """Test that scraper retries on timeout."""
        # First two attempts timeout, third succeeds
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            self._create_mock_response(200, self._create_amazon_html()),
        ]

        scraper = PriceScraper(max_retries=3, retry_delay=1)
        result = scraper.scrape_product("https://amazon.fr/product")

        # Should have made 3 attempts
        assert mock_get.call_count == 3
        # Should have slept twice (after first two failures)
        assert mock_sleep.call_count == 2
        # Should succeed on third attempt
        assert result is not None
        assert result.name == "Test Product"

    @patch('app.services.scraper.requests.get')
    @patch('app.services.scraper.time.sleep')
    def test_retry_exhaustion(self, mock_sleep, mock_get):
        """Test that scraper gives up after max retries."""
        # All attempts timeout
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        scraper = PriceScraper(max_retries=3, retry_delay=1)
        result = scraper.scrape_product("https://amazon.fr/product")

        # Should have made 3 attempts
        assert mock_get.call_count == 3
        # Should return None after exhausting retries
        assert result is None

    @patch('app.services.scraper.requests.get')
    def test_no_retry_on_404(self, mock_get):
        """Test that scraper doesn't retry on 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        scraper = PriceScraper(max_retries=3, retry_delay=1)

        with pytest.raises(ProductUnavailableError):
            scraper.scrape_product("https://amazon.fr/product")

        # Should only attempt once (no retry on 404)
        assert mock_get.call_count == 1

    @patch('app.services.scraper.requests.get')
    @patch('app.services.scraper.time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_get):
        """Test that retry delay increases exponentially."""
        mock_get.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            self._create_mock_response(200, self._create_amazon_html()),
        ]

        scraper = PriceScraper(max_retries=3, retry_delay=2)
        scraper.scrape_product("https://amazon.fr/product")

        # Check that sleep was called with increasing delays (2s, 4s)
        sleep_calls = [call(2), call(4)]
        mock_sleep.assert_has_calls(sleep_calls)

    @staticmethod
    def _create_mock_response(status_code, html_content):
        """Helper to create mock response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.content = html_content.encode('utf-8')
        mock_response.raise_for_status = Mock()
        return mock_response

    @staticmethod
    def _create_amazon_html():
        """Helper to create Amazon HTML."""
        return """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <span class="a-price-whole">99</span>
                <span class="a-price-fraction">99</span>
                <img id="landingImage" src="https://example.com/image.jpg" />
            </body>
        </html>
        """


@pytest.mark.unit
class TestUnavailabilityDetection:
    """Test product unavailability detection."""

    def test_detect_unavailable_generic(self):
        """Test generic unavailability detection."""
        html = """
        <html>
            <body>
                <h1>Product Page</h1>
                <p>Ce produit est actuellement indisponible.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://example.com")
        assert is_unavailable is True

    def test_detect_available_product(self):
        """Test that available products are not flagged."""
        html = """
        <html>
            <body>
                <h1>Product Page</h1>
                <p>Add to cart now!</p>
                <span class="price">99.99 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://example.com")
        assert is_unavailable is False

    def test_detect_out_of_stock_english(self):
        """Test detection of 'out of stock' in English."""
        html = """
        <html>
            <body>
                <h1>Product</h1>
                <div class="availability">Currently out of stock</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://example.com")
        assert is_unavailable is True

    def test_detect_rupture_de_stock(self):
        """Test detection of 'rupture de stock' in French."""
        html = """
        <html>
            <body>
                <h1>Produit</h1>
                <div class="stock">En rupture de stock</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://example.com")
        assert is_unavailable is True

    def test_detect_amazon_unavailability(self):
        """Test Amazon-specific unavailability detection."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <div id="availability">
                    <span>Actuellement indisponible</span>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://amazon.fr/product")
        assert is_unavailable is True

    @patch('app.services.scraper.requests.get')
    def test_unavailable_error_raised(self, mock_get):
        """Test that ProductUnavailableError is raised for unavailable products."""
        html = """
        <html>
            <body>
                <h1>Product</h1>
                <p>Ce produit n'est plus disponible.</p>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scraper = PriceScraper(max_retries=1)

        with pytest.raises(ProductUnavailableError) as exc_info:
            scraper.scrape_product("https://example.com/product")

        assert "no longer available" in str(exc_info.value)


@pytest.mark.unit
class TestLoggingIntegration:
    """Test that logging is properly integrated."""

    @patch('app.services.scraper.logger')
    @patch('app.services.scraper.requests.get')
    def test_logging_on_success(self, mock_get, mock_logger):
        """Test that success is logged."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <span class="a-price-whole">99</span>
                <span class="a-price-fraction">99</span>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scraper = PriceScraper()
        result = scraper.scrape_product("https://amazon.fr/product")

        # Check that info log was called for success
        assert mock_logger.info.called
        assert result is not None

    @patch('app.services.scraper.logger')
    @patch('app.services.scraper.requests.get')
    def test_logging_on_failure(self, mock_get, mock_logger):
        """Test that failures are logged."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        scraper = PriceScraper(max_retries=2)
        result = scraper.scrape_product("https://amazon.fr/product")

        # Check that warning logs were called for retries
        assert mock_logger.warning.called
        # Check that error log was called for final failure
        assert mock_logger.error.called
        assert result is None

    @patch('app.services.scraper.logger')
    @patch('app.services.scraper.requests.get')
    def test_logging_unavailability(self, mock_get, mock_logger):
        """Test that unavailability is logged."""
        html = "<html><body><p>Produit indisponible</p></body></html>"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scraper = PriceScraper(max_retries=1)

        with pytest.raises(ProductUnavailableError):
            scraper.scrape_product("https://example.com/product")

        # Check that warning was logged for unavailability
        assert mock_logger.warning.called
