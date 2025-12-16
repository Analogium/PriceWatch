"""
Unit tests specifically for decimal price parsing.

This test suite ensures that prices with decimals are correctly parsed
across all scrapers and formats (14,34 should become 14.34, not 14.00).
"""

from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

from app.services.scraper import PriceScraper


class TestDecimalPriceParsing:
    """Test suite for decimal price parsing across different formats."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = PriceScraper()

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_decimal_with_comma(self):
        """Test Amazon price with comma separator (14,34)."""
        html = """
        <html>
            <body>
                <span id="productTitle">Product with decimals</span>
                <span class="a-price-whole">14,</span>
                <span class="a-price-fraction">34</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_decimal_with_dot(self):
        """Test Amazon price with dot separator (14.34)."""
        html = """
        <html>
            <body>
                <span id="productTitle">Product with decimals</span>
                <span class="a-price-whole">14.</span>
                <span class="a-price-fraction">34</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_fnac_decimal_with_comma(self):
        """Test Fnac price with comma separator (14,34 €)."""
        html = """
        <html>
            <body>
                <h1 class="f-productHeader-Title">Product</h1>
                <span class="f-priceBox-price">14,34 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_fnac(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_darty_decimal_with_comma(self):
        """Test Darty price with comma separator (14,34 €)."""
        html = """
        <html>
            <body>
                <h1 class="product_title">Product</h1>
                <span class="product_price">14,34 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_darty(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_various_decimal_formats(self):
        """Test various decimal formats across different prices."""
        test_cases = [
            ("14,34", 14.34),
            ("14.34", 14.34),
            ("99,99", 99.99),
            ("1234,56", 1234.56),
            ("9,95", 9.95),
            ("0,99", 0.99),
        ]

        for price_text, expected_price in test_cases:
            html = f"""
            <html>
                <body>
                    <h1 class="f-productHeader-Title">Product</h1>
                    <span class="f-priceBox-price">{price_text} €</span>
                </body>
            </html>
            """
            soup = BeautifulSoup(html, "html.parser")
            result = self.scraper._scrape_fnac(soup)

            assert result is not None, f"Failed to parse price: {price_text}"
            assert (
                result.price == expected_price
            ), f"Price {price_text}: Expected {expected_price} but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_cdiscount_decimal_with_comma(self):
        """Test Cdiscount price with comma separator."""
        html = """
        <html>
            <body>
                <h1 itemprop="name">Product</h1>
                <span class="fpPrice">14,34 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_cdiscount(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_boulanger_decimal_with_comma(self):
        """Test Boulanger price with comma separator."""
        html = """
        <html>
            <body>
                <h1 class="product-title">Product</h1>
                <span class="price">14,34 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_boulanger(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_leclerc_decimal_with_comma(self):
        """Test E.Leclerc price with comma separator."""
        html = """
        <html>
            <body>
                <h1 class="product-name">Product</h1>
                <span class="product-price">14,34 €</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_leclerc(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"
