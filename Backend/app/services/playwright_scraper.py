"""
Playwright-based scraper for e-commerce sites with anti-bot protection.

This scraper uses browser automation to bypass CAPTCHA and Cloudflare protections.
"""

import asyncio
import random
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from app.schemas.product import ProductScrapedData
from app.core.logging_config import get_logger
import re

logger = get_logger(__name__)


class PlaywrightScraper:
    """
    Advanced scraper using Playwright for sites with strong anti-bot protection.

    This scraper launches a real browser (Chromium) to:
    - Execute JavaScript
    - Handle cookies and sessions
    - Bypass CAPTCHA and Cloudflare
    - Appear as a real human user
    """

    def __init__(self, headless: bool = True, timeout: int = 30000, max_retries: int = 2):
        """
        Initialize Playwright scraper.

        Args:
            headless: Run browser in headless mode (no GUI)
            timeout: Timeout in milliseconds for page operations
            max_retries: Maximum number of retries for CAPTCHA/bot detection
        """
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.browser: Optional[Browser] = None

    async def scrape_product(self, url: str) -> Optional[ProductScrapedData]:
        """
        Scrape product using browser automation with retry logic.

        Args:
            url: Product URL to scrape

        Returns:
            ProductScrapedData if successful, None otherwise
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Add random delay between retries (2-5 seconds)
                if attempt > 1:
                    delay = random.uniform(2.0, 5.0)
                    logger.info(f"Playwright retry {attempt}/{self.max_retries} - waiting {delay:.1f}s...")
                    await asyncio.sleep(delay)

                logger.info(f"Playwright scraping attempt {attempt}/{self.max_retries} for: {url}")

                async with async_playwright() as p:
                    # Launch browser
                    browser = await p.chromium.launch(
                        headless=self.headless,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage",
                            "--no-sandbox",
                        ],
                    )

                    # Create context with realistic settings
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        locale="fr-FR",
                        timezone_id="Europe/Paris",
                    )

                    # Create page
                    page = await context.new_page()

                    # Navigate to URL
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout)

                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(2000)

                    # Detect site and scrape accordingly
                    if "amazon" in url.lower():
                        result = await self._scrape_amazon(page)
                    elif "fnac" in url.lower():
                        result = await self._scrape_fnac(page)
                    elif "darty" in url.lower():
                        result = await self._scrape_darty(page)
                    elif "cdiscount" in url.lower():
                        result = await self._scrape_cdiscount(page)
                    elif "boulanger" in url.lower():
                        result = await self._scrape_boulanger(page)
                    elif "leclerc" in url.lower():
                        result = await self._scrape_leclerc(page)
                    else:
                        result = await self._scrape_generic(page)

                    await browser.close()

                if result:
                    logger.info(f"Successfully scraped with Playwright: {result.name} - €{result.price}")
                    return result
                else:
                    logger.warning(f"Playwright scraping returned no data for {url}")
                    last_error = Exception("No data extracted")
                    # Continue to next retry if available

            except PlaywrightTimeoutError as e:
                last_error = e
                logger.warning(f"Playwright timeout on attempt {attempt}/{self.max_retries} for {url}")
                # Continue to next retry if available
            except Exception as e:
                last_error = e
                logger.warning(f"Playwright error on attempt {attempt}/{self.max_retries} for {url}: {str(e)}")
                # Continue to next retry if available

        # All retries exhausted
        logger.error(f"Playwright scraping failed after {self.max_retries} attempts for {url}: {last_error}")
        return None

    async def _scrape_amazon(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape Amazon product page using Playwright."""
        try:
            # Wait longer for Amazon to load (they often have slow JS)
            await page.wait_for_timeout(3000)

            # Try to wait for product title with longer timeout
            try:
                await page.wait_for_selector('#productTitle, h1[id*="title"]', timeout=15000)
            except:
                # If title not found, might be a CAPTCHA or bot detection page
                # Try to detect if it's a bot check page
                captcha_form = await page.query_selector('form[action*="validateCaptcha"]')
                robot_check = await page.query_selector("text=/Robot Check/i")

                if captcha_form or robot_check:
                    logger.error(
                        "Amazon CAPTCHA/Robot Check detected. "
                        "This is a known limitation - Amazon randomly shows CAPTCHAs to detect bots. "
                        "Consider using a different product URL or trying again later."
                    )
                    # Raise exception to trigger retry
                    raise Exception("Amazon CAPTCHA detected")
                # Otherwise continue trying to scrape

            # Extract title
            title_elem = await page.query_selector("#productTitle")
            if not title_elem:
                title_elem = await page.query_selector('h1[id*="title"]')
            name = await title_elem.inner_text() if title_elem else "Unknown Product"
            name = name.strip()

            # Extract price - multiple selectors
            price = None
            price_selectors = [
                ".a-price-whole",
                'span[class*="price-whole"]',
                ".a-price .a-offscreen",
                'span[class*="price"]',
            ]

            for selector in price_selectors:
                try:
                    price_elem = await page.query_selector(selector)
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        # Clean price text
                        price_text = price_text.replace("€", "").replace(",", ".").replace(" ", "").strip()
                        # Extract number
                        match = re.search(r"(\d+[.,]?\d*)", price_text)
                        if match:
                            price = float(match.group(1).replace(",", "."))
                            break
                except:
                    continue

            if not price:
                logger.warning("Failed to extract price from Amazon page")
                return None

            # Extract image
            image = None
            image_selectors = ["#landingImage", 'img[id*="image"]', ".a-dynamic-image"]
            for selector in image_selectors:
                try:
                    image_elem = await page.query_selector(selector)
                    if image_elem:
                        image = await image_elem.get_attribute("src")
                        break
                except:
                    continue

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Amazon page with Playwright: {str(e)}", exc_info=True)
            return None

    async def _scrape_fnac(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape Fnac product page using Playwright."""
        try:
            # Wait for content to load
            await page.wait_for_selector("h1, .f-productHeader-Title", timeout=10000)

            # Extract title
            title_selectors = [".f-productHeader-Title", 'h1[class*="product"]', "h1"]
            name = "Unknown Product"
            for selector in title_selectors:
                try:
                    title_elem = await page.query_selector(selector)
                    if title_elem:
                        name = await title_elem.inner_text()
                        name = name.strip()
                        break
                except:
                    continue

            # Extract price
            price = None
            price_selectors = [
                ".f-priceBox-price",
                'span[class*="price"]',
                '[itemprop="price"]',
            ]

            for selector in price_selectors:
                try:
                    price_elem = await page.query_selector(selector)
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        # Clean and extract price
                        price_text = price_text.replace("€", "").replace(",", ".").replace(" ", "").strip()
                        match = re.search(r"(\d+[.,]?\d*)", price_text)
                        if match:
                            price = float(match.group(1).replace(",", "."))
                            break
                except:
                    continue

            # Try meta tag if direct selectors failed
            if not price:
                try:
                    price_meta = await page.query_selector('meta[itemprop="price"]')
                    if price_meta:
                        price_content = await price_meta.get_attribute("content")
                        if price_content:
                            price = float(price_content)
                except:
                    pass

            if not price:
                logger.warning("Failed to extract price from Fnac page")
                return None

            # Extract image
            image = None
            image_selectors = [".f-productVisuals-mainImage", 'img[class*="product"]', 'img[itemprop="image"]']
            for selector in image_selectors:
                try:
                    image_elem = await page.query_selector(selector)
                    if image_elem:
                        image = await image_elem.get_attribute("src")
                        break
                except:
                    continue

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error parsing Fnac page with Playwright: {str(e)}", exc_info=True)
            return None

    async def _scrape_darty(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape Darty product page using Playwright."""
        return await self._scrape_generic(page)

    async def _scrape_cdiscount(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape Cdiscount product page using Playwright."""
        return await self._scrape_generic(page)

    async def _scrape_boulanger(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape Boulanger product page using Playwright."""
        return await self._scrape_generic(page)

    async def _scrape_leclerc(self, page: Page) -> Optional[ProductScrapedData]:
        """Scrape E.Leclerc product page using Playwright."""
        return await self._scrape_generic(page)

    async def _scrape_generic(self, page: Page) -> Optional[ProductScrapedData]:
        """Generic scraper using common patterns."""
        try:
            # Extract title
            name = "Unknown Product"
            title_selectors = ["h1", '[itemprop="name"]', ".product-title", ".product-name"]
            for selector in title_selectors:
                try:
                    title_elem = await page.query_selector(selector)
                    if title_elem:
                        name = await title_elem.inner_text()
                        name = name.strip()
                        break
                except:
                    continue

            # Extract price
            price = None
            # Try various price selectors
            price_selectors = [
                '[itemprop="price"]',
                ".price",
                '[class*="price"]',
                'meta[itemprop="price"]',
                'meta[property="product:price:amount"]',
            ]

            for selector in price_selectors:
                try:
                    price_elem = await page.query_selector(selector)
                    if price_elem:
                        # Check if it's a meta tag
                        tag_name = await price_elem.evaluate("el => el.tagName.toLowerCase()")
                        if tag_name == "meta":
                            price_content = await price_elem.get_attribute("content")
                            if price_content:
                                price = float(price_content)
                                break
                        else:
                            price_text = await price_elem.inner_text()
                            price_text = price_text.replace("€", "").replace(",", ".").replace(" ", "").strip()
                            match = re.search(r"(\d+[.,]?\d*)", price_text)
                            if match:
                                price = float(match.group(1).replace(",", "."))
                                break
                except:
                    continue

            if not price:
                logger.warning("Generic scraper: Failed to extract price")
                return None

            # Extract image
            image = None
            image_selectors = ['[itemprop="image"]', 'meta[property="og:image"]', 'img[class*="product"]']
            for selector in image_selectors:
                try:
                    image_elem = await page.query_selector(selector)
                    if image_elem:
                        tag_name = await image_elem.evaluate("el => el.tagName.toLowerCase()")
                        if tag_name == "meta":
                            image = await image_elem.get_attribute("content")
                        else:
                            image = await image_elem.get_attribute("src")
                        if image:
                            break
                except:
                    continue

            return ProductScrapedData(name=name, price=price, image=image)

        except Exception as e:
            logger.error(f"Error in generic Playwright scraper: {str(e)}", exc_info=True)
            return None


# Singleton instance
playwright_scraper = PlaywrightScraper()


# Helper function for synchronous usage
def scrape_with_playwright(url: str) -> Optional[ProductScrapedData]:
    """
    Synchronous wrapper for Playwright scraping.

    Args:
        url: Product URL to scrape

    Returns:
        ProductScrapedData if successful, None otherwise
    """
    try:
        return asyncio.run(playwright_scraper.scrape_product(url))
    except Exception as e:
        logger.error(f"Error in sync Playwright wrapper: {str(e)}", exc_info=True)
        return None
