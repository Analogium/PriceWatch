"""
Celery tasks for background jobs.
This file contains the price checking task that runs periodically.
"""

from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.config import settings
from app.db.base import SessionLocal
from app.models.product import Product
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.services.scraper import scraper, ProductUnavailableError
from app.services.email import email_service
from app.services.price_history import price_history_service
from app.core.logging_config import get_logger

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
    "check-prices-daily": {
        "task": "check_all_prices",
        "schedule": 86400.0,  # Run every 24 hours (in seconds)
    },
}
