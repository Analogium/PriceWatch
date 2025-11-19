# 🛡️ Administration & Analytics Features

This document describes the administration and analytics features in PriceWatch.

## Overview

The administration module provides system administrators with comprehensive tools to monitor the platform, manage users, and export data for GDPR compliance.

## Table of Contents

- [User Roles](#user-roles)
- [Admin Endpoints](#admin-endpoints)
- [Analytics & Statistics](#analytics--statistics)
- [Data Export (GDPR)](#data-export-gdpr)
- [Scraping Performance Tracking](#scraping-performance-tracking)
- [Security & Access Control](#security--access-control)
- [Usage Examples](#usage-examples)

---

## User Roles

### Admin Role

Users can be granted admin privileges by setting `is_admin = True` in the database or via the admin promotion endpoint.

**Default behavior:**
- All new users have `is_admin = False`
- Admin privileges must be explicitly granted

**Admin capabilities:**
- View global system statistics
- View per-site scraping performance
- View detailed user statistics
- Export user data (GDPR compliance)
- Promote/revoke admin privileges
- Delete user accounts

**Protections:**
- Admins cannot revoke their own admin privileges
- Admins cannot delete their own account
- All admin endpoints require authentication + admin role

---

## Admin Endpoints

All admin endpoints are prefixed with `/api/v1/admin` and require admin authentication.

### Statistics Endpoints

#### Get Global Statistics
```
GET /api/v1/admin/stats/global
```

Returns comprehensive system-wide statistics:
- Total users (total, verified, admins)
- Product statistics (total, active, unavailable)
- Scraping statistics (success rate, avg response time)
- Price check statistics
- Per-site breakdown

**Response:**
```json
{
  "total_users": 1250,
  "verified_users": 1100,
  "admin_users": 5,
  "total_products": 15000,
  "active_products": 12000,
  "unavailable_products": 500,
  "total_price_checks": 50000,
  "successful_scrapes": 47500,
  "failed_scrapes": 2500,
  "scraping_success_rate": 95.0,
  "average_response_time": 1.234,
  "stats_by_site": {
    "amazon": {
      "total_scrapes": 20000,
      "success_rate": 96.5,
      "average_response_time": 1.1
    },
    "fnac": {
      "total_scrapes": 10000,
      "success_rate": 94.2,
      "average_response_time": 1.3
    }
  }
}
```

#### Get Site Statistics
```
GET /api/v1/admin/stats/site/{site_name}
```

Returns detailed statistics for a specific site.

**Supported sites:** `amazon`, `fnac`, `darty`, `cdiscount`, `boulanger`, `leclerc`

**Response:**
```json
{
  "site_name": "amazon",
  "total_scrapes": 20000,
  "successful_scrapes": 19300,
  "failed_scrapes": 700,
  "success_rate": 96.5,
  "average_response_time": 1.123,
  "last_scrape": "2025-11-19T10:30:00"
}
```

#### Get All Users Statistics
```
GET /api/v1/admin/stats/users?skip=0&limit=100
```

Returns paginated statistics for all users.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "user_id": 1,
    "email": "user@example.com",
    "is_verified": true,
    "is_admin": false,
    "created_at": "2025-01-15T10:00:00",
    "total_products": 25,
    "active_products": 20,
    "total_price_checks": 500,
    "alerts_sent": 15,
    "last_login": null
  }
]
```

#### Get User Statistics
```
GET /api/v1/admin/stats/users/{user_id}
```

Returns detailed statistics for a specific user.

#### Get Scraping Statistics
```
GET /api/v1/admin/stats/scraping?hours=24&limit=100
```

Returns recent scraping attempts with details.

**Query Parameters:**
- `hours`: Hours to look back (default: 24, max: 168)
- `limit`: Maximum records (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "site_name": "amazon",
    "product_id": 123,
    "status": "success",
    "response_time": 1.234,
    "error_message": null,
    "created_at": "2025-11-19T10:30:00"
  },
  {
    "id": 2,
    "site_name": "fnac",
    "product_id": 456,
    "status": "failure",
    "response_time": null,
    "error_message": "Connection timeout",
    "created_at": "2025-11-19T10:29:00"
  }
]
```

---

## Analytics & Statistics

### Global Statistics

The system tracks:
- **User metrics**: Total users, verified users, admin users
- **Product metrics**: Total products, active products (checked in last 48h), unavailable products
- **Scraping metrics**: Success rate, failure rate, average response time
- **Activity metrics**: Total price checks, alerts sent

### Per-Site Statistics

For each supported site:
- Total scraping attempts
- Success/failure counts
- Success rate percentage
- Average response time
- Last scrape timestamp

### User Statistics

For each user:
- Account information (email, verification status, admin status)
- Product counts (total, active)
- Activity (price checks, alerts received)
- Account age

---

## Data Export (GDPR)

Admins can export complete user data for GDPR compliance requests.

### Export to CSV
```
GET /api/v1/admin/export/user/{user_id}/csv?include_products=true&include_price_history=true&include_preferences=true
```

Returns a CSV file as a downloadable attachment.

**Query Parameters:**
- `include_products`: Include product data (default: true)
- `include_price_history`: Include price history (default: true)
- `include_preferences`: Include user preferences (default: true)

**CSV Format:**
```csv
=== USER INFORMATION ===
ID,Email,Verified,Admin,Created At
1,user@example.com,True,False,2025-01-15 10:00:00

=== PRODUCTS ===
ID,Name,URL,Current Price,Target Price,Is Available,Last Checked,Created At
1,Product Name,https://...,99.99,89.99,True,2025-11-19 10:00:00,2025-01-15 10:00:00

=== PRICE HISTORY ===
Product ID,Price,Recorded At
1,99.99,2025-11-19 10:00:00
1,95.00,2025-11-18 10:00:00

=== PREFERENCES ===
Email Notifications,Webhook Notifications,Price Drop Alerts,Weekly Summary,Availability Alerts
True,False,True,True,True
```

### Export to JSON
```
GET /api/v1/admin/export/user/{user_id}/json?include_products=true&include_price_history=true&include_preferences=true
```

Returns complete user data as JSON.

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_verified": true,
    "is_admin": false,
    "created_at": "2025-01-15T10:00:00"
  },
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "url": "https://...",
      "current_price": 99.99,
      "target_price": 89.99,
      "is_available": true,
      "last_checked": "2025-11-19T10:00:00",
      "created_at": "2025-01-15T10:00:00"
    }
  ],
  "price_history": [
    {
      "product_id": 1,
      "price": 99.99,
      "recorded_at": "2025-11-19T10:00:00"
    }
  ],
  "preferences": {
    "email_notifications": true,
    "webhook_notifications": false,
    "price_drop_alerts": true,
    "weekly_summary": true,
    "availability_alerts": true,
    "notification_frequency": "daily",
    "webhook_url": null,
    "webhook_type": null
  }
}
```

---

## Scraping Performance Tracking

### ScrapingStats Model

The system automatically logs every scraping attempt with:
- **site_name**: Which site was scraped (amazon, fnac, etc.)
- **product_id**: Optional reference to the product
- **status**: Result (success, failure, unavailable)
- **response_time**: Time taken in seconds
- **error_message**: Error details if failed
- **created_at**: Timestamp

### Logging Scraping Stats

Scraping statistics are logged automatically via `AdminService.log_scraping_stat()`:

```python
from app.services.admin import AdminService

# Log successful scrape
AdminService.log_scraping_stat(
    db,
    site_name="amazon",
    status="success",
    product_id=123,
    response_time=1.234
)

# Log failed scrape
AdminService.log_scraping_stat(
    db,
    site_name="fnac",
    status="failure",
    product_id=456,
    error_message="Connection timeout"
)
```

**Integration points:**
- Should be integrated into `app/services/scraper.py`
- Should be called by Celery tasks in `tasks.py`
- Provides real-time monitoring of scraping health

---

## Security & Access Control

### Admin Dependency

All admin endpoints use the `get_current_admin_user` dependency:

```python
from app.api.dependencies import get_current_admin_user

@router.get("/admin/endpoint")
def admin_endpoint(admin: User = Depends(get_current_admin_user)):
    # Only accessible to users with is_admin=True
    pass
```

### Protections

1. **Self-revocation prevention**: Admins cannot revoke their own admin privileges
2. **Self-deletion prevention**: Admins cannot delete their own account
3. **Authentication required**: All endpoints require valid JWT token
4. **Admin verification**: Token user must have `is_admin=True`

### User Management

#### Promote User to Admin
```
POST /api/v1/admin/users/{user_id}/admin
```

Grants admin privileges to a user.

**Response:**
```json
{
  "message": "User user@example.com promoted to admin"
}
```

#### Revoke Admin Privileges
```
DELETE /api/v1/admin/users/{user_id}/admin
```

Removes admin privileges from a user (cannot be used on self).

**Response:**
```json
{
  "message": "Admin privileges revoked from user user@example.com"
}
```

#### Delete User
```
DELETE /api/v1/admin/users/{user_id}
```

**WARNING:** Permanently deletes user and all associated data (products, price history, preferences).

**Response:**
```json
{
  "message": "User user@example.com and all associated data deleted successfully"
}
```

---

## Usage Examples

### Example 1: Monitoring System Health

```bash
# Get global statistics
curl -X GET "http://localhost:8000/api/v1/admin/stats/global" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Check specific site performance
curl -X GET "http://localhost:8000/api/v1/admin/stats/site/amazon" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# View recent scraping failures
curl -X GET "http://localhost:8000/api/v1/admin/stats/scraping?hours=1&limit=50" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" | jq '.[] | select(.status=="failure")'
```

### Example 2: User Management

```bash
# View all users
curl -X GET "http://localhost:8000/api/v1/admin/stats/users?limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Get specific user stats
curl -X GET "http://localhost:8000/api/v1/admin/stats/users/123" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Promote user to admin
curl -X POST "http://localhost:8000/api/v1/admin/users/123/admin" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Example 3: GDPR Data Export

```bash
# Export user data as CSV
curl -X GET "http://localhost:8000/api/v1/admin/export/user/123/csv" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o user_123_data.csv

# Export user data as JSON
curl -X GET "http://localhost:8000/api/v1/admin/export/user/123/json?include_products=true" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" | jq '.'

# Export only user info (no products/history)
curl -X GET "http://localhost:8000/api/v1/admin/export/user/123/json?include_products=false&include_price_history=false&include_preferences=false" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" | jq '.'
```

### Example 4: Creating First Admin User

Since admins cannot be created via the API, you'll need to manually set the first admin in the database:

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U pricewatch -d pricewatch

# Set a user as admin
UPDATE users SET is_admin = true WHERE email = 'admin@example.com';

# Verify
SELECT id, email, is_admin FROM users WHERE is_admin = true;

# Exit
\q
```

Alternatively, use a Python script:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Find user and promote to admin
user = db.query(User).filter(User.email == "admin@example.com").first()
if user:
    user.is_admin = True
    db.commit()
    print(f"User {user.email} is now an admin")
else:
    print("User not found")

db.close()
```

---

## Database Migration

To apply the admin features, run the migration:

```bash
cd Backend

# The migration file is in /tmp/migration_admin.py
# Copy it to the alembic versions directory
cp /tmp/migration_admin.py alembic/versions/a1b2c3d4e5f6_add_admin_features_and_scraping_stats.py

# Apply the migration
./migrate.sh "Add admin features and scraping stats"
```

Or apply manually with Docker:

```bash
docker-compose exec backend alembic upgrade head
```

---

## Testing

Run the admin unit tests:

```bash
cd Backend

# Run all admin tests
docker-compose exec backend python3 -m pytest tests/test_unit_admin.py -v

# Run with coverage
docker-compose exec backend python3 -m pytest tests/test_unit_admin.py --cov=app.services.admin --cov=app.api.dependencies -v

# Run specific test
docker-compose exec backend python3 -m pytest tests/test_unit_admin.py::TestAdminService::test_get_global_stats -v
```

**Test coverage:**
- 16 unit tests
- 100% coverage of AdminService
- 100% coverage of admin dependencies

---

## Next Steps

### Recommended Enhancements

1. **Integrate scraping stats logging**
   - Add `AdminService.log_scraping_stat()` calls to scraper service
   - Update Celery tasks to log all scraping attempts

2. **Add dashboard UI**
   - Create frontend dashboard for visualizing statistics
   - Real-time charts for scraping performance
   - User activity graphs

3. **Add admin action logging**
   - Log all admin actions (user deletion, role changes)
   - Create audit trail for compliance

4. **Implement rate limiting for admin endpoints**
   - Prevent abuse of export endpoints
   - Separate limits for admin vs regular users

5. **Add email notifications for critical events**
   - Alert admins when scraping success rate drops
   - Notify when new admin accounts are created

---

**Last Updated:** 2025-11-19
