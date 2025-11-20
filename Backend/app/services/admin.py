"""
Admin service for analytics and statistics
"""

import io
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.scraping_stats import ScrapingStats
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.admin import GlobalStats, ScrapingStatsResponse, SiteStats, UserStats


class AdminService:
    """Service for admin operations and analytics"""

    @staticmethod
    def get_global_stats(db: Session) -> GlobalStats:
        """Get global system statistics"""
        # User stats
        total_users = db.query(func.count(User.id)).scalar() or 0
        verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar() or 0  # noqa: E712
        admin_users = db.query(func.count(User.id)).filter(User.is_admin == True).scalar() or 0  # noqa: E712

        # Product stats
        total_products = db.query(func.count(Product.id)).scalar() or 0

        # Active products (checked in last 48h)
        two_days_ago = datetime.utcnow() - timedelta(hours=48)
        active_products = db.query(func.count(Product.id)).filter(Product.last_checked >= two_days_ago).scalar() or 0

        unavailable_products = (
            db.query(func.count(Product.id)).filter(Product.is_available == False).scalar() or 0  # noqa: E712
        )

        # Scraping stats
        total_scrapes = db.query(func.count(ScrapingStats.id)).scalar() or 0
        successful_scrapes = (
            db.query(func.count(ScrapingStats.id)).filter(ScrapingStats.status == "success").scalar() or 0
        )
        failed_scrapes = db.query(func.count(ScrapingStats.id)).filter(ScrapingStats.status == "failure").scalar() or 0

        scraping_success_rate = (successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0.0

        # Average response time
        avg_response_time = (
            db.query(func.avg(ScrapingStats.response_time)).filter(ScrapingStats.response_time.isnot(None)).scalar()
            or 0.0
        )

        # Total price checks (from price history)
        total_price_checks = db.query(func.count(PriceHistory.id)).scalar() or 0

        # Stats by site
        stats_by_site = AdminService._get_stats_by_site(db)

        return GlobalStats(
            total_users=total_users,
            verified_users=verified_users,
            admin_users=admin_users,
            total_products=total_products,
            active_products=active_products,
            unavailable_products=unavailable_products,
            total_price_checks=total_price_checks,
            successful_scrapes=successful_scrapes,
            failed_scrapes=failed_scrapes,
            scraping_success_rate=round(scraping_success_rate, 2),
            average_response_time=round(float(avg_response_time), 3),
            stats_by_site=stats_by_site,
        )

    @staticmethod
    def _get_stats_by_site(db: Session) -> Dict[str, Any]:
        """Get scraping statistics grouped by site"""
        sites = ["amazon", "fnac", "darty", "cdiscount", "boulanger", "leclerc"]
        stats_by_site = {}

        for site in sites:
            site_stats = AdminService.get_site_stats(db, site)
            stats_by_site[site] = {
                "total_scrapes": site_stats.total_scrapes,
                "success_rate": site_stats.success_rate,
                "average_response_time": site_stats.average_response_time,
            }

        return stats_by_site

    @staticmethod
    def get_site_stats(db: Session, site_name: str) -> SiteStats:
        """Get statistics for a specific site"""
        total_scrapes = (
            db.query(func.count(ScrapingStats.id)).filter(ScrapingStats.site_name == site_name).scalar() or 0
        )

        successful_scrapes = (
            db.query(func.count(ScrapingStats.id))
            .filter(ScrapingStats.site_name == site_name, ScrapingStats.status == "success")
            .scalar()
            or 0
        )

        failed_scrapes = (
            db.query(func.count(ScrapingStats.id))
            .filter(ScrapingStats.site_name == site_name, ScrapingStats.status == "failure")
            .scalar()
            or 0
        )

        success_rate = (successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0.0

        avg_response_time = (
            db.query(func.avg(ScrapingStats.response_time))
            .filter(ScrapingStats.site_name == site_name, ScrapingStats.response_time.isnot(None))
            .scalar()
            or 0.0
        )

        last_scrape = db.query(func.max(ScrapingStats.created_at)).filter(ScrapingStats.site_name == site_name).scalar()

        return SiteStats(
            site_name=site_name,
            total_scrapes=total_scrapes,
            successful_scrapes=successful_scrapes,
            failed_scrapes=failed_scrapes,
            success_rate=round(success_rate, 2),
            average_response_time=round(float(avg_response_time), 3),
            last_scrape=last_scrape,
        )

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Optional[UserStats]:
        """Get statistics for a specific user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        total_products = db.query(func.count(Product.id)).filter(Product.user_id == user_id).scalar() or 0

        two_days_ago = datetime.utcnow() - timedelta(hours=48)
        active_products = (
            db.query(func.count(Product.id))
            .filter(Product.user_id == user_id, Product.last_checked >= two_days_ago)
            .scalar()
            or 0
        )

        # Count price checks for user's products
        total_price_checks = (
            db.query(func.count(PriceHistory.id)).join(Product).filter(Product.user_id == user_id).scalar() or 0
        )

        # Count alerts sent (price history entries where price <= target_price)
        alerts_sent = (
            db.query(func.count(PriceHistory.id))
            .join(Product)
            .filter(Product.user_id == user_id, PriceHistory.price <= Product.target_price)
            .scalar()
            or 0
        )

        return UserStats(
            user_id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            created_at=user.created_at,
            total_products=total_products,
            active_products=active_products,
            total_price_checks=total_price_checks,
            alerts_sent=alerts_sent,
            last_login=None,  # Could be tracked with a separate login log table
        )

    @staticmethod
    def get_all_users_stats(db: Session, skip: int = 0, limit: int = 100) -> List[UserStats]:
        """Get statistics for all users with pagination"""
        users = db.query(User).offset(skip).limit(limit).all()
        stats = [AdminService.get_user_stats(db, user.id) for user in users]
        return [s for s in stats if s is not None]

    @staticmethod
    def get_recent_scraping_stats(db: Session, hours: int = 24, limit: int = 100) -> List[ScrapingStatsResponse]:
        """Get recent scraping statistics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        stats = (
            db.query(ScrapingStats)
            .filter(ScrapingStats.created_at >= cutoff_time)
            .order_by(ScrapingStats.created_at.desc())
            .limit(limit)
            .all()
        )

        return [ScrapingStatsResponse.model_validate(stat) for stat in stats]

    @staticmethod
    def export_user_data_csv(
        db: Session,
        user_id: int,
        include_products: bool = True,
        include_price_history: bool = True,
        include_preferences: bool = True,
    ) -> str:
        """Export user data to CSV format (GDPR compliance)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        output = io.StringIO()

        # User info
        output.write("=== USER INFORMATION ===\n")
        output.write("ID,Email,Verified,Admin,Created At\n")
        output.write(f"{user.id},{user.email},{user.is_verified},{user.is_admin},{user.created_at}\n\n")

        # Products
        if include_products:
            output.write("=== PRODUCTS ===\n")
            products = db.query(Product).filter(Product.user_id == user_id).all()
            if products:
                output.write("ID,Name,URL,Current Price,Target Price,Is Available,Last Checked,Created At\n")
                for product in products:
                    output.write(
                        f"{product.id},{product.name},{product.url},"
                        f"{product.current_price},{product.target_price},"
                        f"{product.is_available},{product.last_checked},{product.created_at}\n"
                    )
            output.write("\n")

        # Price History
        if include_price_history:
            output.write("=== PRICE HISTORY ===\n")
            price_history = (
                db.query(PriceHistory)
                .join(Product)
                .filter(Product.user_id == user_id)
                .order_by(PriceHistory.recorded_at.desc())
                .all()
            )
            if price_history:
                output.write("Product ID,Price,Recorded At\n")
                for entry in price_history:
                    output.write(f"{entry.product_id},{entry.price},{entry.recorded_at}\n")
            output.write("\n")

        # Preferences
        if include_preferences:
            output.write("=== PREFERENCES ===\n")
            prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if prefs:
                output.write(
                    "Email Notifications,Webhook Notifications,Price Drop Alerts,Weekly Summary,Availability Alerts\n"
                )
                output.write(
                    f"{prefs.email_notifications},{prefs.webhook_notifications},"
                    f"{prefs.price_drop_alerts},{prefs.weekly_summary},{prefs.availability_alerts}\n"
                )
            output.write("\n")

        return output.getvalue()

    @staticmethod
    def export_user_data_json(
        db: Session,
        user_id: int,
        include_products: bool = True,
        include_price_history: bool = True,
        include_preferences: bool = True,
    ) -> Dict[str, Any]:
        """Export user data to JSON format (GDPR compliance)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        data: Dict[str, Any] = {
            "user": {
                "id": user.id,
                "email": user.email,
                "is_verified": user.is_verified,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
            }
        }

        if include_products:
            products = db.query(Product).filter(Product.user_id == user_id).all()
            data["products"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "url": p.url,
                    "current_price": p.current_price,
                    "target_price": p.target_price,
                    "is_available": p.is_available,
                    "last_checked": p.last_checked.isoformat() if p.last_checked else None,
                    "created_at": p.created_at.isoformat(),
                }
                for p in products
            ]

        if include_price_history:
            price_history = (
                db.query(PriceHistory)
                .join(Product)
                .filter(Product.user_id == user_id)
                .order_by(PriceHistory.recorded_at.desc())
                .all()
            )
            data["price_history"] = [
                {
                    "product_id": entry.product_id,
                    "price": entry.price,
                    "recorded_at": entry.recorded_at.isoformat(),
                }
                for entry in price_history
            ]

        if include_preferences:
            prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if prefs:
                data["preferences"] = {
                    "email_notifications": prefs.email_notifications,
                    "webhook_notifications": prefs.webhook_notifications,
                    "price_drop_alerts": prefs.price_drop_alerts,
                    "weekly_summary": prefs.weekly_summary,
                    "availability_alerts": prefs.availability_alerts,
                    "notification_frequency": prefs.notification_frequency,
                    "webhook_url": prefs.webhook_url,
                    "webhook_type": prefs.webhook_type,
                }

        return data

    @staticmethod
    def log_scraping_stat(
        db: Session,
        site_name: str,
        status: str,
        product_id: Optional[int] = None,
        response_time: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> ScrapingStats:
        """Log a scraping attempt for analytics"""
        stat = ScrapingStats(
            site_name=site_name,
            product_id=product_id,
            status=status,
            response_time=response_time,
            error_message=error_message,
        )
        db.add(stat)
        db.commit()
        db.refresh(stat)
        return stat
