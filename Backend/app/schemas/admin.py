from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any


class GlobalStats(BaseModel):
    """Global system statistics"""
    total_users: int
    verified_users: int
    admin_users: int
    total_products: int
    active_products: int  # products checked in last 48h
    unavailable_products: int
    total_price_checks: int
    successful_scrapes: int
    failed_scrapes: int
    scraping_success_rate: float
    average_response_time: float
    stats_by_site: Dict[str, Any]


class UserStats(BaseModel):
    """Statistics for a specific user"""
    user_id: int
    email: str
    is_verified: bool
    is_admin: bool
    created_at: datetime
    total_products: int
    active_products: int
    total_price_checks: int
    alerts_sent: int
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ScrapingStatsResponse(BaseModel):
    """Scraping statistics response"""
    id: int
    site_name: str
    product_id: Optional[int]
    status: str
    response_time: Optional[float]
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteStats(BaseModel):
    """Statistics per site"""
    site_name: str
    total_scrapes: int
    successful_scrapes: int
    failed_scrapes: int
    success_rate: float
    average_response_time: float
    last_scrape: Optional[datetime] = None


class ExportRequest(BaseModel):
    """Request to export user data"""
    user_id: int
    include_products: bool = True
    include_price_history: bool = True
    include_preferences: bool = True


class ExportResponse(BaseModel):
    """Response with exported data URL or content"""
    export_id: str
    created_at: datetime
    file_path: str
    file_size: int


class AdminAction(BaseModel):
    """Log of admin actions"""
    admin_id: int
    action_type: str  # delete_user, disable_user, change_role, etc.
    target_user_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
