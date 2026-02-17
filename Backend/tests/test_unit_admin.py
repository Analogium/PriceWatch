"""
Unit tests for admin service and endpoints
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.i18n import t
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.scraping_stats import ScrapingStats
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.schemas.admin import GlobalStats, SiteStats, UserStats
from app.services.admin import AdminService


@pytest.mark.unit
@pytest.mark.admin
class TestAdminService:
    """Test AdminService methods"""

    def test_get_global_stats(self):
        """Test getting global system statistics"""
        # Mock database session
        db = Mock(spec=Session)

        # Create a counter for query calls
        call_count = [0]

        def mock_query_side_effect(*args, **kwargs):
            mock_q = Mock()
            current_call = call_count[0]

            # For queries with filter
            def filter_side_effect(*filter_args, **filter_kwargs):
                mock_f = Mock()
                # Return appropriate value based on call count
                if current_call == 1:  # verified_users
                    mock_f.scalar.return_value = 80
                elif current_call == 2:  # admin_users
                    mock_f.scalar.return_value = 5
                elif current_call == 4:  # active_products
                    mock_f.scalar.return_value = 400
                elif current_call == 5:  # unavailable_products
                    mock_f.scalar.return_value = 20
                elif current_call == 7:  # successful_scrapes
                    mock_f.scalar.return_value = 950
                elif current_call == 8:  # failed_scrapes
                    mock_f.scalar.return_value = 50
                elif current_call == 10:  # avg response time
                    mock_f.scalar.return_value = 1.5
                else:
                    mock_f.scalar.return_value = 0
                return mock_f

            mock_q.filter.side_effect = filter_side_effect

            # For direct scalar calls (no filter)
            if current_call == 0:  # total_users
                mock_q.scalar.return_value = 100
            elif current_call == 3:  # total_products
                mock_q.scalar.return_value = 500
            elif current_call == 6:  # total_scrapes
                mock_q.scalar.return_value = 1000
            elif current_call == 9:  # total_price_checks
                mock_q.scalar.return_value = 5000
            else:
                mock_q.scalar.return_value = 0

            call_count[0] += 1
            return mock_q

        db.query.side_effect = mock_query_side_effect

        # Mock stats by site
        with patch.object(AdminService, "_get_stats_by_site", return_value={}):
            stats = AdminService.get_global_stats(db)

        assert isinstance(stats, GlobalStats)
        assert stats.total_users == 100
        assert stats.verified_users == 80
        assert stats.admin_users == 5
        assert stats.total_products == 500
        assert stats.active_products == 400
        assert stats.unavailable_products == 20
        assert stats.successful_scrapes == 950
        assert stats.failed_scrapes == 50
        assert stats.scraping_success_rate == 95.0
        # Note: total_price_checks and average_response_time may vary due to _get_stats_by_site

    def test_get_site_stats(self):
        """Test getting statistics for a specific site"""
        db = Mock(spec=Session)

        # Create a counter for query calls
        call_count = [0]
        last_scrape_time = datetime.utcnow()

        def mock_query_side_effect(*args, **kwargs):
            mock_q = Mock()
            mock_f = Mock()

            # All queries in get_site_stats use filter
            if call_count[0] == 0:  # total_scrapes
                mock_f.scalar.return_value = 100
            elif call_count[0] == 1:  # successful_scrapes
                mock_f.scalar.return_value = 95
            elif call_count[0] == 2:  # failed_scrapes
                mock_f.scalar.return_value = 5
            elif call_count[0] == 3:  # avg_response_time
                mock_f.scalar.return_value = 1.2
            elif call_count[0] == 4:  # last_scrape
                mock_f.scalar.return_value = last_scrape_time
            else:
                mock_f.scalar.return_value = None

            mock_q.filter.return_value = mock_f
            call_count[0] += 1
            return mock_q

        db.query.side_effect = mock_query_side_effect

        stats = AdminService.get_site_stats(db, "amazon")

        assert isinstance(stats, SiteStats)
        assert stats.site_name == "amazon"
        assert stats.total_scrapes == 100
        assert stats.successful_scrapes == 95
        assert stats.failed_scrapes == 5
        assert stats.success_rate == 95.0
        assert stats.average_response_time == 1.2
        assert stats.last_scrape == last_scrape_time

    def test_get_user_stats_existing_user(self):
        """Test getting statistics for an existing user"""
        db = Mock(spec=Session)

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_verified = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.utcnow()

        # Mock queries
        mock_query = Mock()
        mock_filter = Mock()
        mock_join = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value.scalar.return_value = 10

        mock_filter.scalar.side_effect = [
            5,  # total_products
            4,  # active_products
        ]

        stats = AdminService.get_user_stats(db, 1)

        assert isinstance(stats, UserStats)
        assert stats.user_id == 1
        assert stats.email == "test@example.com"
        assert stats.is_verified is True
        assert stats.is_admin is False

    def test_get_user_stats_nonexistent_user(self):
        """Test getting statistics for a nonexistent user"""
        db = Mock(spec=Session)

        # Mock query returning None
        mock_query = Mock()
        mock_filter = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        stats = AdminService.get_user_stats(db, 999)

        assert stats is None

    def test_get_all_users_stats(self):
        """Test getting statistics for all users with pagination"""
        db = Mock(spec=Session)

        # Mock users
        mock_users = [
            Mock(spec=User, id=1, email="user1@example.com"),
            Mock(spec=User, id=2, email="user2@example.com"),
        ]

        mock_query = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        db.query.return_value = mock_query
        mock_query.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_users

        # Mock get_user_stats calls
        with patch.object(AdminService, "get_user_stats") as mock_get_stats:
            mock_stats = [
                Mock(spec=UserStats, user_id=1),
                Mock(spec=UserStats, user_id=2),
            ]
            mock_get_stats.side_effect = mock_stats

            stats = AdminService.get_all_users_stats(db, skip=0, limit=10)

        assert len(stats) == 2
        assert stats[0].user_id == 1
        assert stats[1].user_id == 2

    def test_get_recent_scraping_stats(self):
        """Test getting recent scraping statistics"""
        db = Mock(spec=Session)

        # Mock scraping stats
        mock_stats = [
            Mock(
                spec=ScrapingStats,
                id=1,
                site_name="amazon",
                product_id=1,
                status="success",
                response_time=1.2,
                error_message=None,
                created_at=datetime.utcnow(),
            ),
            Mock(
                spec=ScrapingStats,
                id=2,
                site_name="fnac",
                product_id=2,
                status="failure",
                response_time=None,
                error_message="Timeout",
                created_at=datetime.utcnow(),
            ),
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_limit = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_stats

        stats = AdminService.get_recent_scraping_stats(db, hours=24, limit=100)

        assert len(stats) == 2

    def test_export_user_data_csv(self):
        """Test exporting user data to CSV format"""
        db = Mock(spec=Session)

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_verified = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.utcnow()

        # Mock products
        mock_products = [
            Mock(
                spec=Product,
                id=1,
                name="Product 1",
                url="https://example.com/1",
                current_price=99.99,
                target_price=89.99,
                is_available=True,
                last_checked=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )
        ]

        # Mock price history
        mock_history = [Mock(spec=PriceHistory, product_id=1, price=99.99, recorded_at=datetime.utcnow())]

        # Mock preferences
        mock_prefs = Mock(
            spec=UserPreferences,
            email_notifications=True,
            webhook_notifications=False,
            price_drop_alerts=True,
            weekly_summary=True,
            availability_alerts=True,
        )

        # Setup query mocks
        mock_query = Mock()
        mock_filter = Mock()
        mock_join = Mock()
        mock_order = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter

        # User query
        mock_filter.first.side_effect = [mock_user, mock_prefs]

        # Products query
        mock_filter.all.side_effect = [mock_products]

        # Price history query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.all.return_value = mock_history

        csv_content = AdminService.export_user_data_csv(
            db, 1, include_products=True, include_price_history=True, include_preferences=True
        )

        assert "USER INFORMATION" in csv_content
        assert "PRODUCTS" in csv_content
        assert "PRICE HISTORY" in csv_content
        assert "PREFERENCES" in csv_content
        assert "test@example.com" in csv_content

    def test_export_user_data_csv_user_not_found(self):
        """Test exporting data for nonexistent user raises error"""
        db = Mock(spec=Session)

        mock_query = Mock()
        mock_filter = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with pytest.raises(ValueError, match="User 999 not found"):
            AdminService.export_user_data_csv(db, 999)

    def test_export_user_data_json(self):
        """Test exporting user data to JSON format"""
        db = Mock(spec=Session)

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_verified = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.utcnow()

        # Mock products
        mock_products = [
            Mock(
                spec=Product,
                id=1,
                name="Product 1",
                url="https://example.com/1",
                current_price=99.99,
                target_price=89.99,
                is_available=True,
                last_checked=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )
        ]

        # Mock price history
        mock_history = [Mock(spec=PriceHistory, product_id=1, price=99.99, recorded_at=datetime.utcnow())]

        # Mock preferences
        mock_prefs = Mock(
            spec=UserPreferences,
            email_notifications=True,
            webhook_notifications=False,
            price_drop_alerts=True,
            weekly_summary=True,
            availability_alerts=True,
            notification_frequency="daily",
            webhook_url=None,
            webhook_type=None,
        )

        # Setup query mocks
        mock_query = Mock()
        mock_filter = Mock()
        mock_join = Mock()
        mock_order = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter

        # User query
        mock_filter.first.side_effect = [mock_user, mock_prefs]

        # Products query
        mock_filter.all.side_effect = [mock_products]

        # Price history query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.all.return_value = mock_history

        json_data = AdminService.export_user_data_json(
            db, 1, include_products=True, include_price_history=True, include_preferences=True
        )

        assert "user" in json_data
        assert json_data["user"]["email"] == "test@example.com"
        assert "products" in json_data
        assert len(json_data["products"]) == 1
        assert "price_history" in json_data
        assert "preferences" in json_data

    def test_export_user_data_json_minimal(self):
        """Test exporting only user info without products/history"""
        db = Mock(spec=Session)

        # Mock user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_verified = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.utcnow()

        mock_query = Mock()
        mock_filter = Mock()

        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        json_data = AdminService.export_user_data_json(
            db, 1, include_products=False, include_price_history=False, include_preferences=False
        )

        assert "user" in json_data
        assert json_data["user"]["email"] == "test@example.com"
        assert "products" not in json_data
        assert "price_history" not in json_data
        assert "preferences" not in json_data

    def test_log_scraping_stat(self):
        """Test logging a scraping statistic"""
        db = Mock(spec=Session)

        # Mock the add, commit, and refresh operations
        mock_stat = Mock(spec=ScrapingStats)
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None

        with patch("app.services.admin.ScrapingStats") as MockScrapingStats:
            MockScrapingStats.return_value = mock_stat

            stat = AdminService.log_scraping_stat(
                db, site_name="amazon", status="success", product_id=1, response_time=1.5, error_message=None
            )

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(mock_stat)

    def test_log_scraping_stat_failure(self):
        """Test logging a failed scraping attempt"""
        db = Mock(spec=Session)

        # Mock the add, commit, and refresh operations
        mock_stat = Mock(spec=ScrapingStats)
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None

        with patch("app.services.admin.ScrapingStats") as MockScrapingStats:
            MockScrapingStats.return_value = mock_stat

            stat = AdminService.log_scraping_stat(
                db,
                site_name="fnac",
                status="failure",
                product_id=2,
                response_time=None,
                error_message="Connection timeout",
            )

        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_site_stats_zero_scrapes(self):
        """Test site stats with zero scrapes (avoid division by zero)"""
        db = Mock(spec=Session)

        # Create a counter for query calls
        call_count = [0]

        def mock_query_side_effect(*args, **kwargs):
            mock_q = Mock()
            mock_f = Mock()

            # All queries return 0 or None for new site
            if call_count[0] == 0:  # total_scrapes
                mock_f.scalar.return_value = 0
            elif call_count[0] == 1:  # successful_scrapes
                mock_f.scalar.return_value = 0
            elif call_count[0] == 2:  # failed_scrapes
                mock_f.scalar.return_value = 0
            elif call_count[0] == 3:  # avg_response_time
                mock_f.scalar.return_value = 0.0
            elif call_count[0] == 4:  # last_scrape
                mock_f.scalar.return_value = None
            else:
                mock_f.scalar.return_value = 0

            mock_q.filter.return_value = mock_f
            call_count[0] += 1
            return mock_q

        db.query.side_effect = mock_query_side_effect

        stats = AdminService.get_site_stats(db, "new_site")

        assert stats.total_scrapes == 0
        assert stats.success_rate == 0.0
        assert stats.average_response_time == 0.0
        assert stats.last_scrape is None

    def test_get_stats_by_site(self):
        """Test getting stats for all sites"""
        db = Mock(spec=Session)

        with patch.object(AdminService, "get_site_stats") as mock_get_site:
            mock_site_stats = Mock(total_scrapes=100, success_rate=95.0, average_response_time=1.2)
            mock_get_site.return_value = mock_site_stats

            stats = AdminService._get_stats_by_site(db)

        assert isinstance(stats, dict)
        assert "amazon" in stats
        assert "fnac" in stats
        assert "darty" in stats
        assert stats["amazon"]["total_scrapes"] == 100
        assert stats["amazon"]["success_rate"] == 95.0


@pytest.mark.unit
@pytest.mark.admin
class TestAdminDependencies:
    """Test admin dependencies"""

    def test_get_current_admin_user_success(self):
        """Test admin dependency with admin user"""
        from app.api.dependencies import get_current_admin_user

        mock_user = Mock(spec=User)
        mock_user.is_admin = True

        result = get_current_admin_user(mock_user)

        assert result is mock_user

    def test_get_current_admin_user_not_admin(self):
        """Test admin dependency with non-admin user raises 403"""
        from fastapi import HTTPException

        from app.api.dependencies import get_current_admin_user

        mock_user = Mock(spec=User)
        mock_user.is_admin = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(mock_user)

        assert exc_info.value.status_code == 403
        assert t("admin_required") in str(exc_info.value.detail)
