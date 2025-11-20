"""Service for managing price history records."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.models.product import Product


class PriceHistoryService:
    """Service to manage price history tracking."""

    @staticmethod
    def record_price(db: Session, product_id: int, price: float) -> PriceHistory:
        """
        Record a new price in the history.

        Args:
            db: Database session
            product_id: ID of the product
            price: Price to record

        Returns:
            Created PriceHistory instance
        """
        price_entry = PriceHistory(product_id=product_id, price=price, recorded_at=datetime.utcnow())
        db.add(price_entry)
        db.commit()
        db.refresh(price_entry)
        return price_entry

    @staticmethod
    def get_product_history(db: Session, product_id: int, limit: Optional[int] = None) -> List[PriceHistory]:
        """
        Get price history for a product.

        Args:
            db: Database session
            product_id: ID of the product
            limit: Optional limit on number of records to return

        Returns:
            List of PriceHistory records, ordered by date (newest first)
        """
        query = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.desc())
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_price_statistics(db: Session, product_id: int) -> dict:
        """
        Calculate price statistics for a product.

        Args:
            db: Database session
            product_id: ID of the product

        Returns:
            Dictionary with statistics (lowest, highest, average, etc.)
        """
        # Get current product info
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        # Calculate statistics from history
        stats = (
            db.query(
                func.min(PriceHistory.price).label("lowest"),
                func.max(PriceHistory.price).label("highest"),
                func.avg(PriceHistory.price).label("average"),
                func.count(PriceHistory.id).label("total"),
            )
            .filter(PriceHistory.product_id == product_id)
            .first()
        )

        if not stats or stats.total == 0:
            # No history yet, use current price
            return {
                "current_price": product.current_price,
                "lowest_price": product.current_price,
                "highest_price": product.current_price,
                "average_price": product.current_price,
                "price_change_percentage": 0.0,
                "total_records": 0,
            }

        # Get first recorded price for change percentage
        first_price = (
            db.query(PriceHistory.price)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.asc())
            .first()
        )

        price_change_percentage = None
        if first_price and first_price[0] > 0:
            price_change = ((product.current_price - first_price[0]) / first_price[0]) * 100
            price_change_percentage = round(price_change, 2)

        return {
            "current_price": product.current_price,
            "lowest_price": float(stats.lowest),
            "highest_price": float(stats.highest),
            "average_price": round(float(stats.average), 2),
            "price_change_percentage": price_change_percentage,
            "total_records": stats.total,
        }

    @staticmethod
    def should_record_price(db: Session, product_id: int, new_price: float) -> bool:
        """
        Determine if we should record this price (avoid duplicates of same price).

        Args:
            db: Database session
            product_id: ID of the product
            new_price: New price to potentially record

        Returns:
            True if the price should be recorded, False otherwise
        """
        # Get the most recent price record
        last_record = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.desc())
            .first()
        )

        # Record if no history exists or if price has changed
        if not last_record or last_record.price != new_price:
            return True

        return False


# Singleton instance
price_history_service = PriceHistoryService()
