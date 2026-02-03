"""
Admin endpoints for analytics and system management
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user, get_db
from app.models.user import User
from app.schemas.admin import GlobalStats, ScrapingStatsResponse, SiteStats, UserStats
from app.services.admin import AdminService

# Path to cookies directory
COOKIES_DIR = Path(__file__).parent.parent.parent.parent / "cookies"
VALID_SITES = ["amazon", "fnac", "darty", "cdiscount", "boulanger", "leclerc"]

router = APIRouter()


@router.get("/stats/global", response_model=GlobalStats)
def get_global_statistics(db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Get global system statistics (admin only)

    Returns:
    - Total users, products, scraping stats
    - Success rates and performance metrics
    - Stats broken down by site
    """
    return AdminService.get_global_stats(db)


@router.get("/stats/site/{site_name}", response_model=SiteStats)
def get_site_statistics(site_name: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Get statistics for a specific site (admin only)

    Supported sites: amazon, fnac, darty, cdiscount, boulanger, leclerc
    """
    valid_sites = ["amazon", "fnac", "darty", "cdiscount", "boulanger", "leclerc"]
    if site_name not in valid_sites:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid site name. Must be one of: {', '.join(valid_sites)}",
        )

    return AdminService.get_site_stats(db, site_name)


@router.get("/stats/users", response_model=List[UserStats])
def get_all_users_statistics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """
    Get statistics for all users with pagination (admin only)

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    return AdminService.get_all_users_stats(db, skip=skip, limit=limit)


@router.get("/stats/users/{user_id}", response_model=UserStats)
def get_user_statistics(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Get statistics for a specific user (admin only)

    Returns:
    - User information
    - Product counts
    - Price check activity
    - Alerts sent
    """
    user_stats = AdminService.get_user_stats(db, user_id)
    if not user_stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user_stats


@router.get("/stats/scraping", response_model=List[ScrapingStatsResponse])
def get_scraping_statistics(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """
    Get recent scraping statistics (admin only)

    Query Parameters:
    - hours: Number of hours to look back (default: 24, max: 168)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    return AdminService.get_recent_scraping_stats(db, hours=hours, limit=limit)


@router.get("/export/user/{user_id}/csv")
def export_user_data_csv(
    user_id: int,
    include_products: bool = Query(True),
    include_price_history: bool = Query(True),
    include_preferences: bool = Query(True),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """
    Export user data in CSV format (admin only, GDPR compliance)

    Query Parameters:
    - include_products: Include product data (default: true)
    - include_price_history: Include price history (default: true)
    - include_preferences: Include user preferences (default: true)

    Returns CSV file as downloadable attachment
    """
    try:
        csv_content = AdminService.export_user_data_csv(
            db,
            user_id,
            include_products=include_products,
            include_price_history=include_price_history,
            include_preferences=include_preferences,
        )

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=user_{user_id}_data.csv"},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/export/user/{user_id}/json")
def export_user_data_json(
    user_id: int,
    include_products: bool = Query(True),
    include_price_history: bool = Query(True),
    include_preferences: bool = Query(True),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """
    Export user data in JSON format (admin only, GDPR compliance)

    Query Parameters:
    - include_products: Include product data (default: true)
    - include_price_history: Include price history (default: true)
    - include_preferences: Include user preferences (default: true)

    Returns complete user data as JSON
    """
    try:
        json_data = AdminService.export_user_data_json(
            db,
            user_id,
            include_products=include_products,
            include_price_history=include_price_history,
            include_preferences=include_preferences,
        )
        return json_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/users/{user_id}/admin")
def promote_user_to_admin(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Promote a user to admin (admin only)

    Grants admin privileges to the specified user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    if user.is_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin")

    user.is_admin = True
    db.commit()

    return {"message": f"User {user.email} promoted to admin"}


@router.delete("/users/{user_id}/admin")
def revoke_admin_privileges(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Revoke admin privileges from a user (admin only)

    Removes admin privileges from the specified user
    """
    # Prevent self-demotion
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot revoke your own admin privileges")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not an admin")

    user.is_admin = False
    db.commit()

    return {"message": f"Admin privileges revoked from user {user.email}"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    """
    Delete a user and all their data (admin only)

    WARNING: This is irreversible. All products, price history,
    and preferences will be permanently deleted.
    """
    # Prevent self-deletion
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account as admin")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    email = user.email
    db.delete(user)
    db.commit()

    return {"message": f"User {email} and all associated data deleted successfully"}


# ============================================================================
# Cookie Management Endpoints
# ============================================================================


@router.get("/cookies")
def get_cookies_status(admin: User = Depends(get_current_admin_user)):
    """
    Get the status of cookies for all supported sites (admin only)

    Returns information about which sites have cookies configured
    and when they were last updated.
    """
    cookies_status = []

    for site in VALID_SITES:
        cookie_file = COOKIES_DIR / f"{site}_cookies.json"
        site_status = {
            "site": site,
            "has_cookies": cookie_file.exists(),
            "cookie_count": 0,
            "last_updated": None,
        }

        if cookie_file.exists():
            try:
                with open(cookie_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                site_status["cookie_count"] = len(cookies) if isinstance(cookies, list) else 0
                # Get file modification time
                mtime = cookie_file.stat().st_mtime
                site_status["last_updated"] = datetime.fromtimestamp(mtime).isoformat()
            except Exception:
                site_status["has_cookies"] = False

        cookies_status.append(site_status)

    return {"cookies": cookies_status}


@router.post("/cookies/{site}")
async def upload_cookies(
    site: str,
    cookies: UploadFile,
    admin: User = Depends(get_current_admin_user),
):
    """
    Upload cookies for a specific site (admin only)

    The cookies file should be a JSON array exported from a browser
    extension like Cookie-Editor.

    Supported sites: amazon, fnac, darty, cdiscount, boulanger, leclerc
    """
    if site not in VALID_SITES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid site. Must be one of: {', '.join(VALID_SITES)}",
        )

    # Read and validate the uploaded file
    try:
        content = await cookies.read()
        cookies_data = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format. Expected a JSON array of cookies.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}",
        )

    # Validate format
    if not isinstance(cookies_data, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Expected a JSON array of cookies.",
        )

    if len(cookies_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cookie array is empty.",
        )

    # Validate each cookie has required fields
    required_fields = {"name", "value", "domain"}
    for i, cookie in enumerate(cookies_data):
        if not isinstance(cookie, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cookie at index {i} is not an object.",
            )
        missing = required_fields - set(cookie.keys())
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cookie at index {i} missing required fields: {', '.join(missing)}",
            )

    # Ensure cookies directory exists
    COOKIES_DIR.mkdir(parents=True, exist_ok=True)

    # Save cookies
    cookie_path = COOKIES_DIR / f"{site}_cookies.json"
    with open(cookie_path, "w", encoding="utf-8") as f:
        json.dump(cookies_data, f, indent=2)

    return {
        "message": f"Cookies for {site} uploaded successfully",
        "site": site,
        "cookie_count": len(cookies_data),
    }


@router.delete("/cookies/{site}")
def delete_cookies(site: str, admin: User = Depends(get_current_admin_user)):
    """
    Delete cookies for a specific site (admin only)

    Supported sites: amazon, fnac, darty, cdiscount, boulanger, leclerc
    """
    if site not in VALID_SITES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid site. Must be one of: {', '.join(VALID_SITES)}",
        )

    cookie_file = COOKIES_DIR / f"{site}_cookies.json"

    if not cookie_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cookies found for {site}",
        )

    cookie_file.unlink()

    return {"message": f"Cookies for {site} deleted successfully", "site": site}


@router.post("/cookies/{site}/test")
async def test_cookies(site: str, admin: User = Depends(get_current_admin_user)):
    """
    Test if cookies for a site are valid by attempting a scrape (admin only)

    This endpoint will attempt to scrape a known product URL to verify
    the cookies are working correctly.

    Supported sites: amazon
    """
    if site not in VALID_SITES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid site. Must be one of: {', '.join(VALID_SITES)}",
        )

    cookie_file = COOKIES_DIR / f"{site}_cookies.json"

    if not cookie_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cookies found for {site}. Upload cookies first.",
        )

    # Test URLs for each site
    test_urls = {
        "amazon": "https://www.amazon.fr/dp/B08N5WRWNW",  # Common product
        "fnac": "https://www.fnac.com/a16608739",
        "darty": "https://www.darty.com/nav/achat/informatique",
        "cdiscount": "https://www.cdiscount.com",
        "boulanger": "https://www.boulanger.com",
        "leclerc": "https://www.e.leclerc",
    }

    test_url = test_urls.get(site)
    if not test_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No test URL configured for {site}",
        )

    # Import here to avoid circular imports
    from app.services.playwright_scraper import PlaywrightScraper

    scraper = PlaywrightScraper(headless=True, timeout=30000, max_retries=1)

    try:
        result = await scraper.scrape_product(test_url)

        if result:
            return {
                "status": "success",
                "message": f"Cookies for {site} are valid",
                "site": site,
                "test_result": {
                    "product_name": result.name[:100] if result.name else None,
                    "price": result.price,
                },
            }
        else:
            return {
                "status": "failed",
                "message": f"Cookies for {site} may be expired or invalid. Scraping returned no data.",
                "site": site,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing cookies: {str(e)}",
            "site": site,
        }
