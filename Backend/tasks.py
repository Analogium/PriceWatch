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
from app.services.scraper import scraper
from app.services.email import email_service

# Initialize Celery
celery_app = Celery(
    "pricewatch",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

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

        for product in products:
            try:
                # Scrape current price
                scraped_data = scraper.scrape_product(product.url)

                if scraped_data:
                    old_price = product.current_price
                    new_price = scraped_data.price

                    # Update product
                    product.current_price = new_price
                    product.last_checked = datetime.utcnow()

                    # Check if price dropped below target
                    if new_price <= product.target_price and old_price > product.target_price:
                        # Get user email
                        user = db.query(User).filter(User.id == product.user_id).first()
                        if user:
                            # Send alert email
                            email_service.send_price_alert(
                                user.email,
                                product.name,
                                new_price,
                                old_price,
                                product.url
                            )
                            print(f"Alert sent for product {product.id}: {product.name}")

                    db.commit()

            except Exception as e:
                print(f"Error checking product {product.id}: {str(e)}")
                continue

        print(f"Price check completed for {len(products)} products")

    finally:
        db.close()


@celery_app.task(name="check_single_product")
def check_single_product(product_id: int):
    """Check price for a single product."""
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            print(f"Product {product_id} not found")
            return

        scraped_data = scraper.scrape_product(product.url)

        if scraped_data:
            old_price = product.current_price
            new_price = scraped_data.price

            product.current_price = new_price
            product.last_checked = datetime.utcnow()

            if new_price <= product.target_price and old_price > product.target_price:
                user = db.query(User).filter(User.id == product.user_id).first()
                if user:
                    email_service.send_price_alert(
                        user.email,
                        product.name,
                        new_price,
                        old_price,
                        product.url
                    )

            db.commit()
            print(f"Product {product_id} checked successfully")

    finally:
        db.close()


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'check-prices-daily': {
        'task': 'check_all_prices',
        'schedule': 86400.0,  # Run every 24 hours (in seconds)
    },
}
