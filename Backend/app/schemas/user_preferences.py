from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class UserPreferencesBase(BaseModel):
    """Base schema for user preferences"""

    email_notifications: bool = True
    webhook_notifications: bool = False
    webhook_url: Optional[str] = None
    price_drop_alerts: bool = True
    weekly_summary: bool = False
    webhook_type: Optional[Literal["slack", "discord", "custom"]] = None
    language: str = "fr"


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences"""

    pass


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)"""

    email_notifications: Optional[bool] = None
    webhook_notifications: Optional[bool] = None
    webhook_url: Optional[str] = None
    price_drop_alerts: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    webhook_type: Optional[Literal["slack", "discord", "custom"]] = None
    language: Optional[Literal["fr", "en"]] = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate webhook URL format"""
        if v is not None and v.strip():
            if not v.startswith(("http://", "https://")):
                raise ValueError("Webhook URL must start with http:// or https://")
        return v


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for returning user preferences"""

    id: int
    user_id: int

    class Config:
        from_attributes = True
