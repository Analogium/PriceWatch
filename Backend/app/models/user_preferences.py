from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Notification channels
    email_notifications: Mapped[bool] = mapped_column(default=True)
    webhook_notifications: Mapped[bool] = mapped_column(default=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For Slack, Discord, etc.

    # Email preferences
    price_drop_alerts: Mapped[bool] = mapped_column(default=True)
    weekly_summary: Mapped[bool] = mapped_column(default=False)

    # Webhook type (for future extension)
    # Options: "slack", "discord", "custom"
    webhook_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="preferences")
