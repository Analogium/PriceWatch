"""
Admin endpoints for analytics and system management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.dependencies import get_current_admin_user, get_db
from app.models.user import User
from app.services.admin import AdminService
from app.schemas.admin import (
    GlobalStats,
    UserStats,
    SiteStats,
    ScrapingStatsResponse,
)

router = APIRouter()


@router.get("/stats/global", response_model=GlobalStats)
def get_global_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get global system statistics (admin only)

    Returns:
    - Total users, products, scraping stats
    - Success rates and performance metrics
    - Stats broken down by site
    """
    return AdminService.get_global_stats(db)


@router.get("/stats/site/{site_name}", response_model=SiteStats)
def get_site_statistics(
    site_name: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get statistics for a specific site (admin only)

    Supported sites: amazon, fnac, darty, cdiscount, boulanger, leclerc
    """
    valid_sites = ["amazon", "fnac", "darty", "cdiscount", "boulanger", "leclerc"]
    if site_name not in valid_sites:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid site name. Must be one of: {', '.join(valid_sites)}"
        )

    return AdminService.get_site_stats(db, site_name)


@router.get("/stats/users", response_model=List[UserStats])
def get_all_users_statistics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Get statistics for all users with pagination (admin only)

    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    return AdminService.get_all_users_stats(db, skip=skip, limit=limit)


@router.get("/stats/users/{user_id}", response_model=UserStats)
def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user_stats


@router.get("/stats/scraping", response_model=List[ScrapingStatsResponse])
def get_scraping_statistics(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
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
    admin: User = Depends(get_current_admin_user)
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
            include_preferences=include_preferences
        )

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=user_{user_id}_data.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/export/user/{user_id}/json")
def export_user_data_json(
    user_id: int,
    include_products: bool = Query(True),
    include_price_history: bool = Query(True),
    include_preferences: bool = Query(True),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
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
            include_preferences=include_preferences
        )
        return json_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/users/{user_id}/admin")
def promote_user_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Promote a user to admin (admin only)

    Grants admin privileges to the specified user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )

    user.is_admin = True
    db.commit()

    return {"message": f"User {user.email} promoted to admin"}


@router.delete("/users/{user_id}/admin")
def revoke_admin_privileges(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Revoke admin privileges from a user (admin only)

    Removes admin privileges from the specified user
    """
    # Prevent self-demotion
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke your own admin privileges"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )

    user.is_admin = False
    db.commit()

    return {"message": f"Admin privileges revoked from user {user.email}"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """
    Delete a user and all their data (admin only)

    WARNING: This is irreversible. All products, price history,
    and preferences will be permanently deleted.
    """
    # Prevent self-deletion
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account as admin"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    email = user.email
    db.delete(user)
    db.commit()

    return {"message": f"User {email} and all associated data deleted successfully"}
