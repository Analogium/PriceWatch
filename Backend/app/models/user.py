from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user_preferences import UserPreferences


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, index=True)
    auth_provider: Mapped[str] = mapped_column(String, default="local")
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    products: Mapped[list["Product"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
