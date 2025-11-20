from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Notification channels
    email_notifications = Column(Boolean, default=True, nullable=False)
    webhook_notifications = Column(Boolean, default=False, nullable=False)
    webhook_url = Column(String, nullable=True)  # For Slack, Discord, etc.

    # Notification frequency
    # Options: "instant", "daily", "weekly"
    notification_frequency = Column(String, default="instant", nullable=False)

    # Email preferences
    price_drop_alerts = Column(Boolean, default=True, nullable=False)
    weekly_summary = Column(Boolean, default=False, nullable=False)
    availability_alerts = Column(Boolean, default=True, nullable=False)

    # Webhook type (for future extension)
    # Options: "slack", "discord", "custom"
    webhook_type = Column(String, nullable=True)

    # Relationship
    user = relationship("User", back_populates="preferences")
