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

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_picks_main_price_not_other_seller(self):
        """Test that Amazon scraper picks the main product price, not another seller's price.

        Regression test: the scraper used to pick the first .a-price-whole on the page,
        which could be a different seller's price (e.g., 10.79 instead of 13.99).
        """
        html = """
        <html>
            <body>
                <span id="productTitle">Lampe Torche LED</span>
                <!-- Other seller price that appears first in DOM -->
                <div id="olp-upd-new">
                    <span class="a-price">
                        <span class="a-offscreen">10,79 €</span>
                        <span class="a-price-whole">10,</span>
                        <span class="a-price-fraction">79</span>
                    </span>
                </div>
                <!-- Main product price in core price container -->
                <div id="corePrice_feature_div">
                    <span class="a-price">
                        <span class="a-offscreen">13,99 €</span>
                        <span class="a-price-whole">13,</span>
                        <span class="a-price-fraction">99</span>
                    </span>
                </div>
                <img id="landingImage" src="https://example.com/image.jpg" />
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 13.99, f"Expected main price 13.99 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_picks_main_price_with_subscribe_save(self):
        """Test that Amazon scraper ignores Subscribe & Save price."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <!-- Subscribe & Save price appears first -->
                <div id="snsPrice">
                    <span class="a-price">
                        <span class="a-offscreen">11,49 €</span>
                        <span class="a-price-whole">11,</span>
                        <span class="a-price-fraction">49</span>
                    </span>
                </div>
                <!-- Main product price -->
                <div id="corePrice_feature_div">
                    <span class="a-price">
                        <span class="a-offscreen">13,99 €</span>
                        <span class="a-price-whole">13,</span>
                        <span class="a-price-fraction">99</span>
                    </span>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 13.99, f"Expected 13.99 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_offscreen_price_preferred(self):
        """Test that .a-offscreen selector is preferred for price extraction."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <div id="corePrice_feature_div">
                    <span class="a-price">
                        <span class="a-offscreen">14,34 €</span>
                        <span class="a-price-whole">14,</span>
                        <span class="a-price-fraction">34</span>
                    </span>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 14.34, f"Expected 14.34 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_corePriceDisplay_desktop_container(self):
        """Test price extraction from corePriceDisplay_desktop_feature_div container."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <div id="corePriceDisplay_desktop_feature_div">
                    <span class="a-price">
                        <span class="a-offscreen">29,99 €</span>
                    </span>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 29.99, f"Expected 29.99 but got {result.price}"

    @pytest.mark.unit
    @pytest.mark.scraper
    def test_amazon_fallback_to_unscoped_search(self):
        """Test that scraper falls back to unscoped search when no container is found."""
        html = """
        <html>
            <body>
                <span id="productTitle">Test Product</span>
                <span class="a-price-whole">99,</span>
                <span class="a-price-fraction">99</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper._scrape_amazon(soup)

        assert result is not None
        assert result.price == 99.99, f"Expected 99.99 but got {result.price}"
