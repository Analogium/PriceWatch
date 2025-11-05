import requests
from bs4 import BeautifulSoup
from typing import Optional
from app.schemas.product import ProductScrapedData
import re


class PriceScraper:
    """Service for scraping product information from e-commerce websites."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_product(self, url: str) -> Optional[ProductScrapedData]:
        """
        Scrape product information from a URL.
        Supports Amazon, Fnac, Darty and other common e-commerce sites.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Detect site and use appropriate scraping strategy
            if 'amazon' in url.lower():
                return self._scrape_amazon(soup)
            elif 'fnac' in url.lower():
                return self._scrape_fnac(soup)
            elif 'darty' in url.lower():
                return self._scrape_darty(soup)
            else:
                # Generic scraping strategy
                return self._scrape_generic(soup)

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def _scrape_amazon(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Amazon product page."""
        try:
            # Title
            title_elem = soup.find('span', {'id': 'productTitle'})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price (Amazon has multiple price formats)
            price = None
            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})

            if price_whole:
                price_str = price_whole.text.strip().replace(',', '.').replace(' ', '')
                if price_fraction:
                    price_str += price_fraction.text.strip()
                price = float(re.sub(r'[^\d.]', '', price_str))

            # Image
            image_elem = soup.find('img', {'id': 'landingImage'})
            image = image_elem.get('src') if image_elem else None

            if price is None:
                return None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            print(f"Error parsing Amazon page: {str(e)}")
            return None

    def _scrape_fnac(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Fnac product page."""
        try:
            # Title
            title_elem = soup.find('h1', {'class': 'f-productHeader-Title'})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price_elem = soup.find('span', {'class': 'f-priceBox-price'})
            if price_elem:
                price_str = price_elem.text.strip().replace('€', '').replace(',', '.').replace(' ', '')
                price = float(re.sub(r'[^\d.]', '', price_str))
            else:
                return None

            # Image
            image_elem = soup.find('img', {'class': 'f-productVisuals-mainImage'})
            image = image_elem.get('src') if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            print(f"Error parsing Fnac page: {str(e)}")
            return None

    def _scrape_darty(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Darty product page."""
        try:
            # Title
            title_elem = soup.find('h1', {'class': 'product_title'})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price_elem = soup.find('span', {'class': 'product_price'})
            if price_elem:
                price_str = price_elem.text.strip().replace('€', '').replace(',', '.').replace(' ', '')
                price = float(re.sub(r'[^\d.]', '', price_str))
            else:
                return None

            # Image
            image_elem = soup.find('img', {'class': 'product_image'})
            image = image_elem.get('src') if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            print(f"Error parsing Darty page: {str(e)}")
            return None

    def _scrape_generic(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Generic scraping strategy for unknown sites."""
        try:
            # Try to find title from common patterns
            name = "Unknown Product"
            for tag in ['h1', 'title']:
                elem = soup.find(tag)
                if elem:
                    name = elem.text.strip()
                    break

            # Try to find price from meta tags or common patterns
            price = None
            price_meta = soup.find('meta', {'property': 'product:price:amount'})
            if price_meta:
                price = float(price_meta.get('content'))

            # Try to find image
            image = None
            image_meta = soup.find('meta', {'property': 'og:image'})
            if image_meta:
                image = image_meta.get('content')

            if price is None:
                return None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            print(f"Error in generic scraping: {str(e)}")
            return None


scraper = PriceScraper()
