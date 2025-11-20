"""
Unit tests for the PriceScraper service.

Tests include:
- Amazon scraping logic
- Fnac scraping logic
- Darty scraping logic
- Generic scraping logic
- Error handling
- Price parsing edge cases
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from app.services.scraper import PriceScraper, scraper


class TestPriceScraper:
    """Test suite for PriceScraper class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = PriceScraper()

    @pytest.mark.unit
    def test_scraper_initialization(self):
        """Test that scraper initializes with correct headers."""
        assert self.scraper is not None
        assert "User-Agent" in self.scraper.headers
        assert "Mozilla" in self.scraper.headers["User-Agent"]

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_amazon_success(self):
        """Test successful Amazon product scraping."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product Amazon</span>
                <span class="a-price-whole">99,</span>
                <span class="a-price-fraction">99</span>
                <img id="landingImage" src="https://example.com/image.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.name == "Test Product Amazon"
        assert result.price == 99.99
        assert result.image == "https://example.com/image.jpg"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_amazon_missing_price(self):
        """Test Amazon scraping with missing price."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <img id="landingImage" src="https://example.com/image.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is None

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_amazon_price_variations(self):
        """Test Amazon price parsing with different formats."""
        # Test with comma separator
        html = """
        <html>
            <body>
                <span id="productTitle">Product</span>
                <span class="a-price-whole">1 234,</span>
                <span class="a-price-fraction">56</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 1234.56

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_fnac_success(self):
        """Test successful Fnac product scraping."""
        html = """
        <html>
            <body>
                <h1 class="f-productHeader-Title">Test Product Fnac</h1>
                <span class="f-priceBox-price">79,99 €</span>
                <img class="f-productVisuals-mainImage" src="https://example.com/fnac.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_fnac(soup)

        assert result is not None
        assert result.name == "Test Product Fnac"
        assert result.price == 79.99
        assert result.image == "https://example.com/fnac.jpg"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_fnac_missing_price(self):
        """Test Fnac scraping with missing price."""
        html = """
        <html>
            <body>
                <h1 class="f-productHeader-Title">Test Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_fnac(soup)

        assert result is None

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_darty_success(self):
        """Test successful Darty product scraping."""
        html = """
        <html>
            <body>
                <h1 class="product_title">Test Product Darty</h1>
                <span class="product_price">149,99 €</span>
                <img class="product_image" src="https://example.com/darty.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_darty(soup)

        assert result is not None
        assert result.name == "Test Product Darty"
        assert result.price == 149.99
        assert result.image == "https://example.com/darty.jpg"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_generic_with_meta_tags(self):
        """Test generic scraping using meta tags."""
        html = """
        <html>
            <head>
                <title>Generic Product</title>
                <meta property="product:price:amount" content="59.99" />
                <meta property="og:image" content="https://example.com/generic.jpg" />
            </head>
            <body>
                <h1>Generic Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_generic(soup)

        assert result is not None
        assert result.price == 59.99
        assert result.image == "https://example.com/generic.jpg"
        assert "Generic Product" in result.name

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_generic_missing_price(self):
        """Test generic scraping with missing price."""
        html = """
        <html>
            <head>
                <title>Product Without Price</title>
            </head>
            <body>
                <h1>Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_generic(soup)

        assert result is None

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_product_amazon_url(self):
        """Test scrape_product with Amazon URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <span id="productTitle">Amazon Product</span>
                <span class="a-price-whole">99,</span>
                <span class="a-price-fraction">99</span>
            </body>
        </html>
        """

        # Mock the session.get method
        self.scraper.session.get = Mock(return_value=mock_response)

        result = self.scraper.scrape_product("https://www.amazon.fr/product/test")

        assert result is not None
        assert result.name == "Amazon Product"
        assert result.price == 99.99
        self.scraper.session.get.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_product_fnac_url(self):
        """Test scrape_product with Fnac URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = """
        <html>
            <body>
                <h1 class="f-productHeader-Title">Fnac Product</h1>
                <span class="f-priceBox-price">79,99</span>
            </body>
        </html>
        """.encode(
            "utf-8"
        )

        # Mock the session.get method
        self.scraper.session.get = Mock(return_value=mock_response)

        result = self.scraper.scrape_product("https://www.fnac.com/product/test")

        assert result is not None
        assert result.name == "Fnac Product"
        assert result.price == 79.99

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_product_darty_url(self):
        """Test scrape_product with Darty URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = """
        <html>
            <body>
                <h1 class="product_title">Darty Product</h1>
                <span class="product_price">149,99</span>
            </body>
        </html>
        """.encode(
            "utf-8"
        )

        # Mock the session.get method
        self.scraper.session.get = Mock(return_value=mock_response)

        result = self.scraper.scrape_product("https://www.darty.com/product/test")

        assert result is not None
        assert result.name == "Darty Product"
        assert result.price == 149.99

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_scrape_product_generic_url(self):
        """Test scrape_product with generic URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <head>
                <title>Generic Product</title>
                <meta property="product:price:amount" content="59.99" />
            </head>
        </html>
        """

        # Mock the session.get method
        self.scraper.session.get = Mock(return_value=mock_response)

        result = self.scraper.scrape_product("https://www.example.com/product/test")

        assert result is not None
        assert result.price == 59.99

    @pytest.mark.unit
    @pytest.mark.scraper
    @patch("app.services.scraper.requests.get")
    def test_scrape_product_http_error(self, mock_get):
        """Test scrape_product with HTTP error."""
        mock_get.side_effect = Exception("Connection error")

        result = self.scraper.scrape_product("https://www.example.com/product/test")

        assert result is None

    @pytest.mark.unit
    @pytest.mark.scraper
    @patch("app.services.scraper.requests.get")
    def test_scrape_product_timeout(self, mock_get):
        """Test scrape_product with timeout."""
        mock_get.side_effect = Exception("Timeout")

        result = self.scraper.scrape_product("https://www.example.com/product/test")

        assert result is None

    @pytest.mark.unit
    @pytest.mark.scraper
    @patch("app.services.scraper.requests.get")
    def test_scrape_product_invalid_html(self, mock_get):
        """Test scrape_product with invalid HTML."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Invalid content</body></html>"
        mock_get.return_value = mock_response

        result = self.scraper.scrape_product("https://www.amazon.fr/product/test")

        # Should return None when no price is found
        assert result is None

    @pytest.mark.unit
    def test_singleton_scraper_instance(self):
        """Test that scraper singleton is correctly instantiated."""
        assert scraper is not None
        assert isinstance(scraper, PriceScraper)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
