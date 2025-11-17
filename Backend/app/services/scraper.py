import requests
from bs4 import BeautifulSoup
from typing import Optional, Callable
from app.schemas.product import ProductScrapedData
import re
import time
import random
from urllib.parse import urlparse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ProductUnavailableError(Exception):
    """Raised when a product is no longer available."""

    pass


class SiteDetector:
    """Utility class for detecting e-commerce sites from URLs."""

    # Site patterns: domain keywords -> site name
    SITE_PATTERNS = {
        "amazon": ["amazon.fr", "amazon.com", "amazon.de", "amazon.co.uk", "amazon.es", "amazon.it"],
        "fnac": ["fnac.com", "fnac.fr"],
        "darty": ["darty.com"],
        "cdiscount": ["cdiscount.com"],
        "boulanger": ["boulanger.com", "boulanger.fr"],
        "leclerc": ["e.leclerc", "e-leclerc"],
    }

    @classmethod
    def detect_site(cls, url: str) -> Optional[str]:
        """
        Detect the e-commerce site from URL.

        Args:
            url: Product URL

        Returns:
            Site name (lowercase) or None if unknown
        """
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc

            # Remove 'www.' prefix if present
            domain = domain.replace("www.", "")

            # Check each site pattern
            for site_name, patterns in cls.SITE_PATTERNS.items():
                for pattern in patterns:
                    if pattern in domain:
                        logger.debug(f"Detected site '{site_name}' from domain '{domain}'")
                        return site_name

            logger.debug(f"Unknown site from domain '{domain}'")
            return None

        except Exception as e:
            logger.warning(f"Error detecting site from URL {url}: {str(e)}")
            return None


class PriceScraper:
    """Service for scraping product information from e-commerce websites."""

    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize scraper with retry logic.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay in seconds between retries
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_product(self, url: str) -> Optional[ProductScrapedData]:
        """
        Scrape product information from a URL with retry logic.
        Supports Amazon, Fnac, Darty and other common e-commerce sites.

        Args:
            url: Product URL to scrape

        Returns:
            ProductScrapedData if successful, None otherwise

        Raises:
            ProductUnavailableError: If product is no longer available
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Scraping attempt {attempt}/{self.max_retries} for URL: {url}")

                # Add random delay to appear more human-like
                if attempt > 1:
                    delay = random.uniform(1.0, 3.0)
                    time.sleep(delay)

                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                # Check for product availability
                if self._is_product_unavailable(soup, url):
                    logger.warning(f"Product unavailable at URL: {url}")
                    raise ProductUnavailableError(f"Product is no longer available: {url}")

                # Detect site automatically and use appropriate scraping strategy
                site = SiteDetector.detect_site(url)

                if site == "amazon":
                    result = self._scrape_amazon(soup)
                elif site == "fnac":
                    result = self._scrape_fnac(soup)
                elif site == "darty":
                    result = self._scrape_darty(soup)
                elif site == "cdiscount":
                    result = self._scrape_cdiscount(soup)
                elif site == "boulanger":
                    result = self._scrape_boulanger(soup)
                elif site == "leclerc":
                    result = self._scrape_leclerc(soup)
                else:
                    # Generic scraping strategy for unknown sites
                    logger.info(f"Using generic scraper for unknown site: {url}")
                    result = self._scrape_generic(soup)

                if result:
                    logger.info(f"Successfully scraped {url}: {result.name} - €{result.price}")
                    return result
                else:
                    logger.warning(f"Failed to extract product data from {url}")
                    # For sites that might need JavaScript rendering, mark as extraction failure
                    last_exception = Exception(f"Failed to extract data from {url}")
                    continue

            except ProductUnavailableError:
                # Don't retry if product is unavailable
                raise

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt} for {url}: {str(e)}")

            except requests.exceptions.HTTPError as e:
                last_exception = e
                status_code = e.response.status_code if e.response else None
                logger.warning(f"HTTP error {status_code} on attempt {attempt} for {url}")

                # Don't retry on 404 or 410 (gone)
                if status_code in [404, 410]:
                    logger.error(f"Product not found (HTTP {status_code}): {url}")
                    raise ProductUnavailableError(f"Product not found: {url}")

                # For 403, add longer delay before retry (anti-bot protection)
                if status_code == 403:
                    logger.warning(f"Access forbidden (403) - possible anti-bot protection on {url}")
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * attempt * 2  # Double the wait time for 403
                        logger.info(f"Waiting {wait_time}s before retry (anti-bot delay)...")
                        time.sleep(wait_time)

            except Exception as e:
                last_exception = e
                logger.warning(f"Error on attempt {attempt} for {url}: {str(e)}")

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = self.retry_delay * attempt
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        # All retries failed - try Playwright as fallback
        if last_exception:
            # Check if it's a 403 error or failed extraction (likely anti-bot)
            should_try_playwright = False

            if isinstance(last_exception, requests.exceptions.HTTPError):
                status_code = last_exception.response.status_code if last_exception.response is not None else None
                if status_code == 403:
                    logger.warning(f"HTTP 403 detected for {url} - trying Playwright fallback")
                    should_try_playwright = True
            elif "Failed to extract data" in str(last_exception):
                # Extraction failed - might need JavaScript rendering
                logger.warning(f"Data extraction failed for {url} - trying Playwright fallback")
                should_try_playwright = True

            # Try Playwright fallback for anti-bot protection
            if should_try_playwright:
                try:
                    logger.info(f"Attempting Playwright fallback for {url}")
                    from app.services.playwright_scraper import scrape_with_playwright

                    result = scrape_with_playwright(url)
                    if result:
                        logger.info(f"Playwright fallback successful for {url}")
                        return result
                    else:
                        logger.error(f"Playwright fallback also failed for {url}")
                except Exception as e:
                    logger.error(f"Playwright fallback error for {url}: {str(e)}")

            # Log final failure
            if isinstance(last_exception, requests.exceptions.HTTPError):
                status_code = last_exception.response.status_code if last_exception.response is not None else None
                if status_code == 403:
                    logger.error(
                        f"Unable to scrape {url} even with Playwright. " f"Site has very strong anti-bot protection."
                    )
                else:
                    logger.error(f"All {self.max_retries} scraping attempts failed for {url}: {last_exception}")
            else:
                logger.error(f"All {self.max_retries} scraping attempts failed for {url}: {last_exception}")

        return None

    def _is_product_unavailable(self, soup: BeautifulSoup, url: str) -> bool:
        """
        Check if product is unavailable (out of stock or discontinued).

        Args:
            soup: BeautifulSoup object of the page
            url: Product URL

        Returns:
            True if product is unavailable, False otherwise
        """
        # Common unavailable indicators
        unavailable_texts = [
            "actuellement indisponible",
            "out of stock",
            "rupture de stock",
            "produit indisponible",
            "n'est plus disponible",
            "no longer available",
            "temporarily out of stock",
            "épuisé",
            "sold out",
            "article supprimé",
            "page introuvable",
            "404",
        ]

        # Check page text for unavailable indicators
        page_text = soup.get_text().lower()
        for indicator in unavailable_texts:
            if indicator in page_text:
                logger.info(f"Found unavailability indicator: '{indicator}' in {url}")
                return True

        # Amazon-specific checks
        if "amazon" in url.lower():
            availability_elem = soup.find("div", {"id": "availability"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "unavailable" in availability_text or "indisponible" in availability_text:
                    return True

            # Check for "Currently unavailable" message
            unavailable_msg = soup.find("span", {"class": "a-size-medium a-color-price"})
            if unavailable_msg and "indisponible" in unavailable_msg.get_text().lower():
                return True

        # Fnac-specific checks
        if "fnac" in url.lower():
            availability_elem = soup.find("div", {"class": "f-productHeader-buyingArea"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "indisponible" in availability_text or "épuisé" in availability_text:
                    return True

        # Darty-specific checks
        if "darty" in url.lower():
            availability_elem = soup.find("div", {"class": "product_availability"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "indisponible" in availability_text or "rupture" in availability_text:
                    return True

        # Use site detector for better site detection
        site = SiteDetector.detect_site(url)

        # Site-specific checks using detector
        if site == "cdiscount":
            availability_elem = soup.find("div", {"class": "fpStockAvailability"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "indisponible" in availability_text or "stock épuisé" in availability_text:
                    return True

        elif site == "boulanger":
            availability_elem = soup.find("div", {"class": "availability"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "indisponible" in availability_text or "épuisé" in availability_text:
                    return True

        elif site == "leclerc":
            availability_elem = soup.find("span", {"class": "stock-status"})
            if availability_elem:
                availability_text = availability_elem.get_text().lower()
                if "indisponible" in availability_text or "rupture" in availability_text:
                    return True

        return False

    def _scrape_amazon(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Amazon product page."""
        try:
            # Title
            title_elem = soup.find("span", {"id": "productTitle"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price (Amazon has multiple price formats)
            price = None
            price_whole = soup.find("span", {"class": "a-price-whole"})
            price_fraction = soup.find("span", {"class": "a-price-fraction"})

            if price_whole:
                price_str = price_whole.text.strip().replace(",", ".").replace(" ", "")
                if price_fraction:
                    price_str += price_fraction.text.strip()
                price = float(re.sub(r"[^\d.]", "", price_str))

            # Image
            image_elem = soup.find("img", {"id": "landingImage"})
            image = image_elem.get("src") if image_elem else None

            if price is None:
                logger.warning("Failed to extract price from Amazon page")
                return None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Amazon page: {str(e)}", exc_info=True)
            return None

    def _scrape_fnac(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Fnac product page."""
        try:
            # Title
            title_elem = soup.find("h1", {"class": "f-productHeader-Title"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price_elem = soup.find("span", {"class": "f-priceBox-price"})
            if price_elem:
                price_str = price_elem.text.strip().replace("€", "").replace(",", ".").replace(" ", "")
                price = float(re.sub(r"[^\d.]", "", price_str))
            else:
                logger.warning("Failed to extract price from Fnac page")
                return None

            # Image
            image_elem = soup.find("img", {"class": "f-productVisuals-mainImage"})
            image = image_elem.get("src") if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Fnac page: {str(e)}", exc_info=True)
            return None

    def _scrape_darty(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Darty product page."""
        try:
            # Title
            title_elem = soup.find("h1", {"class": "product_title"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price_elem = soup.find("span", {"class": "product_price"})
            if price_elem:
                price_str = price_elem.text.strip().replace("€", "").replace(",", ".").replace(" ", "")
                price = float(re.sub(r"[^\d.]", "", price_str))
            else:
                logger.warning("Failed to extract price from Darty page")
                return None

            # Image
            image_elem = soup.find("img", {"class": "product_image"})
            image = image_elem.get("src") if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Darty page: {str(e)}", exc_info=True)
            return None

    def _scrape_generic(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Generic scraping strategy for unknown sites."""
        try:
            # Try to find title from common patterns
            name = "Unknown Product"
            for tag in ["h1", "title"]:
                elem = soup.find(tag)
                if elem:
                    name = elem.text.strip()
                    break

            # Try to find price from meta tags or common patterns
            price = None
            price_meta = soup.find("meta", {"property": "product:price:amount"})
            if price_meta:
                price = float(price_meta.get("content"))

            # Try to find image
            image = None
            image_meta = soup.find("meta", {"property": "og:image"})
            if image_meta:
                image = image_meta.get("content")

            if price is None:
                logger.warning("Failed to extract price using generic scraper")
                return None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error in generic scraping: {str(e)}", exc_info=True)
            return None

    def _scrape_cdiscount(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Cdiscount product page."""
        try:
            # Title
            title_elem = soup.find("h1", {"itemprop": "name"})
            if not title_elem:
                title_elem = soup.find("h1", {"class": "fpDesCol1"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price - Cdiscount has various price formats
            price = None
            price_elem = soup.find("span", {"class": "fpPrice"})
            if not price_elem:
                price_elem = soup.find("span", {"itemprop": "price"})
            if not price_elem:
                price_elem = soup.find("meta", {"itemprop": "price"})
                if price_elem:
                    price_str = price_elem.get("content", "")
                else:
                    price_str = ""
            else:
                price_str = price_elem.text.strip()

            if price_str:
                price_str = price_str.replace("€", "").replace(",", ".").replace(" ", "")
                price = float(re.sub(r"[^\d.]", "", price_str))

            if price is None:
                logger.warning("Failed to extract price from Cdiscount page")
                return None

            # Image
            image_elem = soup.find("img", {"class": "img", "itemprop": "image"})
            if not image_elem:
                image_elem = soup.find("meta", {"property": "og:image"})
                image = image_elem.get("content") if image_elem else None
            else:
                image = image_elem.get("src") if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Cdiscount page: {str(e)}", exc_info=True)
            return None

    def _scrape_boulanger(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape Boulanger product page."""
        try:
            # Title
            title_elem = soup.find("h1", {"class": "product-title"})
            if not title_elem:
                title_elem = soup.find("h1", {"itemprop": "name"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price = None
            price_elem = soup.find("span", {"class": "price"})
            if not price_elem:
                price_elem = soup.find("meta", {"itemprop": "price"})
                if price_elem:
                    price_str = price_elem.get("content", "")
                else:
                    price_str = ""
            else:
                price_str = price_elem.text.strip()

            if price_str:
                price_str = price_str.replace("€", "").replace(",", ".").replace(" ", "")
                price = float(re.sub(r"[^\d.]", "", price_str))

            if price is None:
                logger.warning("Failed to extract price from Boulanger page")
                return None

            # Image
            image_elem = soup.find("img", {"class": "product-visual__image"})
            if not image_elem:
                image_elem = soup.find("meta", {"property": "og:image"})
                image = image_elem.get("content") if image_elem else None
            else:
                image = image_elem.get("src") if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Boulanger page: {str(e)}", exc_info=True)
            return None

    def _scrape_leclerc(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
        """Scrape E.Leclerc product page."""
        try:
            # Title
            title_elem = soup.find("h1", {"class": "product-name"})
            if not title_elem:
                title_elem = soup.find("h1", {"itemprop": "name"})
            name = title_elem.text.strip() if title_elem else "Unknown Product"

            # Price
            price = None
            price_elem = soup.find("span", {"class": "product-price"})
            if not price_elem:
                price_elem = soup.find("meta", {"itemprop": "price"})
                if price_elem:
                    price_str = price_elem.get("content", "")
                else:
                    price_str = ""
            else:
                price_str = price_elem.text.strip()

            if price_str:
                price_str = price_str.replace("€", "").replace(",", ".").replace(" ", "")
                price = float(re.sub(r"[^\d.]", "", price_str))

            if price is None:
                logger.warning("Failed to extract price from E.Leclerc page")
                return None

            # Image
            image_elem = soup.find("img", {"class": "product-image"})
            if not image_elem:
                image_elem = soup.find("meta", {"property": "og:image"})
                image = image_elem.get("content") if image_elem else None
            else:
                image = image_elem.get("src") if image_elem else None

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing E.Leclerc page: {str(e)}", exc_info=True)
            return None


scraper = PriceScraper()
