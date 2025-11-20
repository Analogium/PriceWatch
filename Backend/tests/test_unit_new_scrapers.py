"""
Unit tests for new scraper functions (Cdiscount, Boulanger, Leclerc).
"""

import pytest
from unittest.mock import Mock
from bs4 import BeautifulSoup

from app.services.scraper import PriceScraper


@pytest.mark.unit
@pytest.mark.scraper
class TestCdiscountScraper:
    """Test Cdiscount scraping functionality."""

    def test_scrape_cdiscount_success(self):
        """Test successful Cdiscount scraping."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">iPad Mini 6 64Go Gris Sidéral</h1>
                <span class="fpPrice">599,99 €</span>
                <img class="img" itemprop="image" src="https://example.com/ipad.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_cdiscount(soup)

        assert result is not None
        assert result.name == "iPad Mini 6 64Go Gris Sidéral"
        assert result.price == 599.99
        assert result.image == "https://example.com/ipad.jpg"

    def test_scrape_cdiscount_meta_price(self):
        """Test Cdiscount scraping with meta price."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Test Product</h1>
                <meta itemprop="price" content="149.99" />
                <meta property="og:image" content="https://example.com/product.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_cdiscount(soup)

        assert result is not None
        assert result.price == 149.99

    def test_scrape_cdiscount_missing_price(self):
        """Test Cdiscount scraping with missing price."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Test Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_cdiscount(soup)

        assert result is None


@pytest.mark.unit
@pytest.mark.scraper
class TestBoulangerScraper:
    """Test Boulanger scraping functionality."""

    def test_scrape_boulanger_success(self):
        """Test successful Boulanger scraping."""
        html = """
        <html>
            <body>
                <h1 class="product-title">MacBook Pro 16"</h1>
                <span class="price">2499,00 €</span>
                <img class="product-visual__image" src="https://example.com/macbook.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_boulanger(soup)

        assert result is not None
        assert result.name == 'MacBook Pro 16"'
        assert result.price == 2499.00
        assert result.image == "https://example.com/macbook.jpg"

    def test_scrape_boulanger_with_meta_price(self):
        """Test Boulanger scraping with meta price tag."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Test Product</h1>
                <meta itemprop="price" content="199.99" />
                <meta property="og:image" content="https://example.com/image.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_boulanger(soup)

        assert result is not None
        assert result.price == 199.99

    def test_scrape_boulanger_missing_price(self):
        """Test Boulanger scraping with missing price."""
        html = """
        <html>
            <body>
                <h1 class="product-title">Test Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_boulanger(soup)

        assert result is None


@pytest.mark.unit
@pytest.mark.scraper
class TestLeclercScraper:
    """Test E.Leclerc scraping functionality."""

    def test_scrape_leclerc_success(self):
        """Test successful E.Leclerc scraping."""
        html = """
        <html>
            <body>
                <h1 class="product-name">Lait demi-écrémé Bio 1L</h1>
                <span class="product-price">1,25 €</span>
                <img class="product-image" src="https://example.com/lait.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_leclerc(soup)

        assert result is not None
        assert result.name == "Lait demi-écrémé Bio 1L"
        assert result.price == 1.25
        assert result.image == "https://example.com/lait.jpg"

    def test_scrape_leclerc_with_meta_price(self):
        """Test E.Leclerc scraping with meta price."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Test Product</h1>
                <meta itemprop="price" content="9.99" />
                <meta property="og:image" content="https://example.com/product.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_leclerc(soup)

        assert result is not None
        assert result.price == 9.99

    def test_scrape_leclerc_missing_price(self):
        """Test E.Leclerc scraping with missing price."""
        html = """
        <html>
            <body>
                <h1 class="product-name">Test Product</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        scraper = PriceScraper()

        result = scraper._scrape_leclerc(soup)

        assert result is None


@pytest.mark.unit
@pytest.mark.scraper
class TestScraperSiteRouting:
    """Test that scraper correctly routes to site-specific scrapers."""

    def test_cdiscount_url_uses_cdiscount_scraper(self):
        """Test that Cdiscount URL uses Cdiscount scraper."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Test Product</h1>
                <span class="fpPrice">99,99 €</span>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        # Mock the session.get method
        scraper.session.get = Mock(return_value=mock_response)

        result = scraper.scrape_product("https://www.cdiscount.com/product/123")

        assert result is not None
        assert result.price == 99.99

    def test_boulanger_url_uses_boulanger_scraper(self):
        """Test that Boulanger URL uses Boulanger scraper."""
        html = """
        <html>
            <body>
                <h1 class="product-title">Test Product</h1>
                <span class="price">199,99 €</span>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        # Mock the session.get method
        scraper.session.get = Mock(return_value=mock_response)

        result = scraper.scrape_product("https://www.boulanger.com/ref/123")

        assert result is not None
        assert result.price == 199.99

    def test_leclerc_url_uses_leclerc_scraper(self):
        """Test that E.Leclerc URL uses Leclerc scraper."""
        html = """
        <html>
            <body>
                <h1 class="product-name">Test Product</h1>
                <span class="product-price">5,99 €</span>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        # Mock the session.get method
        scraper.session.get = Mock(return_value=mock_response)

        result = scraper.scrape_product("https://www.e.leclerc/product/123")

        assert result is not None
        assert result.price == 5.99

    def test_unknown_url_uses_generic_scraper(self):
        """Test that unknown URL uses generic scraper."""
        html = """
        <html>
            <head>
                <title>Test Product</title>
                <meta property="product:price:amount" content="29.99" />
                <meta property="og:image" content="https://example.com/image.jpg" />
            </head>
        </html>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html.encode("utf-8")
        mock_response.raise_for_status = Mock()

        scraper = PriceScraper(max_retries=1)
        # Mock the session.get method
        scraper.session.get = Mock(return_value=mock_response)

        result = scraper.scrape_product("https://www.unknownsite.com/product/123")

        assert result is not None
        assert result.price == 29.99
