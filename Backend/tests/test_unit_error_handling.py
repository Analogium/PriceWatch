"""
Unit tests for error handling features (logging, retry logic, unavailability detection).
"""

from unittest.mock import Mock, patch

import pytest
import requests
from bs4 import BeautifulSoup

from app.services.scraper import PriceScraper, ProductUnavailableError


@pytest.mark.unit
class TestRetryLogic:
    """Test retry logic in scraper."""

    @patch("app.services.scraper.time.sleep")
    def test_retry_on_timeout(self, mock_sleep):
        """Test that scraper retries on timeout."""
        scraper = PriceScraper(max_retries=3, retry_delay=1)

        # Mock session.get to raise timeout, then succeed
        scraper.session.get = Mock(
            side_effect=[
                requests.exceptions.Timeout("Timeout 1"),
                requests.exceptions.Timeout("Timeout 2"),
                self._create_mock_response(200, self._create_amazon_html()),
            ]
        )

        result = scraper.scrape_product("https://amazon.fr/product")

        # Should have made 3 attempts
        assert scraper.session.get.call_count == 3
        # Should have slept at least twice (random delay + retry delay after failures)
        assert mock_sleep.call_count >= 2
        # Should succeed on third attempt
        assert result is not None
        assert result.name == "Test Product"

    @patch("app.services.scraper.time.sleep")
    def test_retry_exhaustion(self, mock_sleep):
        """Test that scraper gives up after max retries."""
        scraper = PriceScraper(max_retries=3, retry_delay=1)

        # All attempts timeout
        scraper.session.get = Mock(side_effect=requests.exceptions.Timeout("Timeout"))

        result = scraper.scrape_product("https://amazon.fr/product")

        # Should have made 3 attempts
        assert scraper.session.get.call_count == 3
        # Should return None after exhausting retries
        assert result is None

    def test_no_retry_on_404(self):
        """Test that scraper doesn't retry on 404 errors."""
        scraper = PriceScraper(max_retries=3, retry_delay=1)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        scraper.session.get = Mock(return_value=mock_response)

        with pytest.raises(ProductUnavailableError):
            scraper.scrape_product("https://amazon.fr/product")

        # Should only attempt once (no retry on 404)
        assert scraper.session.get.call_count == 1

    @patch("app.services.scraper.time.sleep")
    @patch("app.services.scraper.random.uniform")
    def test_exponential_backoff(self, mock_uniform, mock_sleep):
        """Test that retry mechanism includes delays."""
        # Mock random.uniform to return fixed value for predictable testing
        mock_uniform.return_value = 1.5

        scraper = PriceScraper(max_retries=3, retry_delay=2)

        scraper.session.get = Mock(
            side_effect=[
                requests.exceptions.Timeout("Timeout 1"),
                requests.exceptions.Timeout("Timeout 2"),
                self._create_mock_response(200, self._create_amazon_html()),
            ]
        )

        result = scraper.scrape_product("https://amazon.fr/product")

        # Check that sleep was called multiple times (for random delays between retries)
        assert mock_sleep.call_count >= 2
        # Verify we eventually succeeded
        assert result is not None

    @staticmethod
    def _create_mock_response(status_code, html_content):
        """Helper to create mock response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.content = html_content.encode("utf-8")
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
        soup = BeautifulSoup(html, "html.parser")
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
        soup = BeautifulSoup(html, "html.parser")
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
        soup = BeautifulSoup(html, "html.parser")
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
        soup = BeautifulSoup(html, "html.parser")
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
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        is_unavailable = scraper._is_product_unavailable(soup, "https://amazon.fr/product")
        assert is_unavailable is True

    def test_unavailable_error_raised(self):
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
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        scraper.session.get = Mock(return_value=mock_response)

        with pytest.raises(ProductUnavailableError) as exc_info:
            scraper.scrape_product("https://example.com/product")

        assert "no longer available" in str(exc_info.value)


@pytest.mark.unit
class TestLoggingIntegration:
    """Test that logging is properly integrated."""

    @patch("app.services.scraper.logger")
    def test_logging_on_success(self, mock_logger):
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
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper()
        scraper.session.get = Mock(return_value=mock_response)

        result = scraper.scrape_product("https://amazon.fr/product")

        # Check that info log was called for success
        assert mock_logger.info.called
        assert result is not None

    @patch("app.services.scraper.logger")
    def test_logging_on_failure(self, mock_logger):
        """Test that failures are logged."""
        scraper = PriceScraper(max_retries=2)
        scraper.session.get = Mock(side_effect=requests.exceptions.Timeout("Timeout"))

        result = scraper.scrape_product("https://amazon.fr/product")

        # Check that warning logs were called for retries
        assert mock_logger.warning.called
        # Check that error log was called for final failure
        assert mock_logger.error.called
        assert result is None

    @patch("app.services.scraper.logger")
    def test_logging_unavailability(self, mock_logger):
        """Test that unavailability is logged."""
        html = "<html><body><p>Produit indisponible</p></body></html>"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        scraper.session.get = Mock(return_value=mock_response)

        with pytest.raises(ProductUnavailableError):
            scraper.scrape_product("https://example.com/product")

        # Check that warning was logged for unavailability
        assert mock_logger.warning.called
