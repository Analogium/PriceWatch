"""
Celery tasks for background jobs.
This file contains the price checking task that runs periodically.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.db.base import SessionLocal
from app.models.product import Product
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.services.email import email_service
from app.services.price_history import price_history_service
from app.services.scraper import ProductUnavailableError, scraper

logger = get_logger(__name__)

# Initialize Celery
celery_app = Celery("pricewatch", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="check_all_prices")
def check_all_prices():
    """
    Check prices for all products and send alerts if price dropped.
    This task should be scheduled to run daily (or more frequently).
    DEPRECATED: Use check_prices_by_frequency instead for frequency-based checking.
    """
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        logger.info(f"Starting price check for {len(products)} products")

        checked_count = 0
        unavailable_count = 0
        error_count = 0

        for product in products:
            try:
                logger.info(f"Checking product {product.id}: {product.name}")

                # Scrape current price
                scraped_data = scraper.scrape_product(product.url)

                if scraped_data:
                    old_price = product.current_price
                    new_price = scraped_data.price

                    # Mark product as available if it was previously unavailable
                    if not product.is_available:
                        logger.info(f"Product {product.id} is available again!")
                        product.is_available = True
                        product.unavailable_since = None

                    # Update product
                    product.current_price = new_price
                    product.last_checked = datetime.utcnow()

                    # Record price in history if it has changed
                    if price_history_service.should_record_price(db, product.id, new_price):
                        price_history_service.record_price(db, product.id, new_price)

                    # Check if price dropped below target
                    if new_price <= product.target_price and old_price > product.target_price:
                        # Get user and their preferences
                        user = db.query(User).filter(User.id == product.user_id).first()
                        if user:
                            # Get user preferences
                            preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()

                            # Send alert email (respecting user preferences)
                            email_service.send_price_alert(
                                user.email,
                                product.name,
                                new_price,
                                old_price,
                                product.url,
                                user_preferences=preferences,
                            )
                            logger.info(f"Alert sent for product {product.id}: {product.name}")

                    db.commit()
                    checked_count += 1

            except ProductUnavailableError as e:
                logger.warning(f"Product {product.id} is unavailable: {str(e)}")
                # Mark product as unavailable
                if product.is_available:
                    product.is_available = False
                    product.unavailable_since = datetime.utcnow()
                    product.last_checked = datetime.utcnow()
                    db.commit()
                    logger.info(f"Marked product {product.id} as unavailable")
                unavailable_count += 1
                continue

            except Exception as e:
                logger.error(f"Error checking product {product.id}: {str(e)}", exc_info=True)
                error_count += 1
                continue

        logger.info(
            f"Price check completed: {checked_count} checked, {unavailable_count} unavailable, {error_count} errors"
        )

    finally:
        db.close()


def scrape_single_product_safe(product: Product) -> Tuple[Product, Optional[float], Optional[Exception]]:
    """
    Safely scrape a single product and return the result.
    This function is thread-safe and designed to be used with ThreadPoolExecutor.

    Args:
        product: Product instance to scrape

    Returns:
        Tuple of (product, new_price, exception)
        - product: The product that was scraped
        - new_price: The scraped price, or None if scraping failed
        - exception: The exception if scraping failed, or None if successful
    """
    try:
        scraped_data = scraper.scrape_product(product.url)
        if scraped_data:
            return (product, scraped_data.price, None)
        return (product, None, Exception("No data returned from scraper"))
    except ProductUnavailableError as e:
        return (product, None, e)
    except Exception as e:
        return (product, None, e)


def scrape_products_parallel(
    products: List[Product], max_workers: int = None
) -> List[Tuple[Product, Optional[float], Optional[Exception]]]:
    """
    Scrape multiple products in parallel using ThreadPoolExecutor.

    Args:
        products: List of Product instances to scrape
        max_workers: Maximum number of concurrent workers (default: settings.MAX_PARALLEL_SCRAPERS)

    Returns:
        List of tuples (product, new_price, exception) for each product
    """
    if max_workers is None:
        max_workers = settings.MAX_PARALLEL_SCRAPERS

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scraping tasks
        future_to_product = {executor.submit(scrape_single_product_safe, product): product for product in products}

        # Collect results as they complete
        for future in as_completed(future_to_product):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # This should rarely happen as scrape_single_product_safe catches exceptions
                product = future_to_product[future]
                logger.error(f"Unexpected error in parallel scraping for product {product.id}: {str(e)}")
                results.append((product, None, e))

    return results


def calculate_priority(product: Product) -> float:
    """
    Calculate priority score for a product based on proximity to target price.
    Lower score = higher priority (should be checked first).

    Priority is based on the percentage distance from current price to target price:
    - Products already below target get highest priority (score = 0)
    - Products close to target get higher priority
    - Products far from target get lower priority

    Args:
        product: Product instance

    Returns:
        float: Priority score (0 = highest priority)
    """
    if product.current_price <= product.target_price:
        # Already below target - highest priority to detect further drops
        return 0.0

    # Calculate percentage above target
    # Example: current=110, target=100 -> 10% above -> score = 0.1
    percentage_above = (product.current_price - product.target_price) / product.target_price
    return percentage_above


@celery_app.task(name="check_prices_by_frequency")
def check_prices_by_frequency(frequency_hours: int):
    """
    Check prices for products with the specified check_frequency.
    Only checks products that haven't been checked in the last 'frequency_hours' hours.
    Products are checked in priority order (closest to target price first).

    Args:
        frequency_hours: The check frequency (6, 12, or 24 hours)
    """
    db: Session = SessionLocal()
    try:
        # Calculate the cutoff time (products not checked in the last X hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=frequency_hours)

        # Query products with this frequency that need checking
        products = (
            db.query(Product)
            .filter(Product.check_frequency == frequency_hours)
            .filter(Product.last_checked <= cutoff_time)
            .all()
        )

        # Sort products by priority (closest to target first)
        products_sorted = sorted(products, key=calculate_priority)

        logger.info(
            f"Starting price check for {len(products_sorted)} products with {frequency_hours}h frequency "
            f"(sorted by priority, using parallel scraping)"
        )

        checked_count = 0
        unavailable_count = 0
        error_count = 0

        # Process products in batches for parallel scraping
        batch_size = settings.SCRAPING_BATCH_SIZE
        for i in range(0, len(products_sorted), batch_size):
            batch = products_sorted[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} products)")

            # Scrape all products in this batch in parallel
            scraping_results = scrape_products_parallel(batch)

            # Process results
            for product, new_price, exception in scraping_results:
                if exception is not None:
                    # Handle scraping errors
                    if isinstance(exception, ProductUnavailableError):
                        logger.warning(f"Product {product.id} is unavailable: {str(exception)}")
                        # Mark product as unavailable
                        if product.is_available:
                            product.is_available = False
                            product.unavailable_since = datetime.utcnow()
                            product.last_checked = datetime.utcnow()
                            db.commit()
                            logger.info(f"Marked product {product.id} as unavailable")
                        unavailable_count += 1
                    else:
                        logger.error(f"Error scraping product {product.id}: {str(exception)}")
                        error_count += 1
                    continue

                # Successful scraping - process the result
                if new_price is not None:
                    logger.info(f"Scraped product {product.id}: {product.name} = €{new_price}")
                    old_price = product.current_price

                    # Mark product as available if it was previously unavailable
                    if not product.is_available:
                        logger.info(f"Product {product.id} is available again!")
                        product.is_available = True
                        product.unavailable_since = None

                    # Update product
                    product.current_price = new_price
                    product.last_checked = datetime.utcnow()

                    # Record price in history if it has changed
                    if price_history_service.should_record_price(db, product.id, new_price):
                        price_history_service.record_price(db, product.id, new_price)

                    # Check if price dropped below target
                    if new_price <= product.target_price and old_price > product.target_price:
                        # Get user and their preferences
                        user = db.query(User).filter(User.id == product.user_id).first()
                        if user:
                            # Get user preferences
                            preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()

                            # Send alert email (respecting user preferences)
                            email_service.send_price_alert(
                                user.email,
                                product.name,
                                new_price,
                                old_price,
                                product.url,
                                user_preferences=preferences,
                            )
                            logger.info(f"Alert sent for product {product.id}: {product.name}")

                    db.commit()
                    checked_count += 1

        logger.info(
            f"Price check ({frequency_hours}h) completed: {checked_count} checked, "
            f"{unavailable_count} unavailable, {error_count} errors"
        )

    finally:
        db.close()


@celery_app.task(name="check_single_product")
def check_single_product(product_id: int):
    """Check price for a single product."""
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            logger.warning(f"Product {product_id} not found")
            return

        logger.info(f"Checking single product {product_id}: {product.name}")

        try:
            scraped_data = scraper.scrape_product(product.url)

            if scraped_data:
                old_price = product.current_price
                new_price = scraped_data.price

                # Mark product as available if it was previously unavailable
                if not product.is_available:
                    logger.info(f"Product {product_id} is available again!")
                    product.is_available = True
                    product.unavailable_since = None

                product.current_price = new_price
                product.last_checked = datetime.utcnow()

                # Record price in history if it has changed
                if price_history_service.should_record_price(db, product.id, new_price):
                    price_history_service.record_price(db, product.id, new_price)

                if new_price <= product.target_price and old_price > product.target_price:
                    user = db.query(User).filter(User.id == product.user_id).first()
                    if user:
                        # Get user preferences
                        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()

                        email_service.send_price_alert(
                            user.email, product.name, new_price, old_price, product.url, user_preferences=preferences
                        )
                        logger.info(f"Alert sent for product {product_id}")

                db.commit()
                logger.info(f"Product {product_id} checked successfully: €{new_price}")

        except ProductUnavailableError as e:
            logger.warning(f"Product {product_id} is unavailable: {str(e)}")
            # Mark product as unavailable
            if product.is_available:
                product.is_available = False
                product.unavailable_since = datetime.utcnow()
                product.last_checked = datetime.utcnow()
                db.commit()
                logger.info(f"Marked product {product_id} as unavailable")

        except Exception as e:
            logger.error(f"Error checking product {product_id}: {str(e)}", exc_info=True)

    finally:
        db.close()


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "check-prices-6h": {
        "task": "check_prices_by_frequency",
        "schedule": 21600.0,  # Run every 6 hours (in seconds)
        "args": (6,),  # Check products with 6h frequency
    },
    "check-prices-12h": {
        "task": "check_prices_by_frequency",
        "schedule": 43200.0,  # Run every 12 hours (in seconds)
        "args": (12,),  # Check products with 12h frequency
    },
    "check-prices-24h": {
        "task": "check_prices_by_frequency",
        "schedule": 86400.0,  # Run every 24 hours (in seconds)
        "args": (24,),  # Check products with 24h frequency
    },
}
