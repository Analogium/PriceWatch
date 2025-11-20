from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.price_history import PriceHistory
    from app.models.user import User


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_price: Mapped[float] = mapped_column()
    target_price: Mapped[float] = mapped_column()
    last_checked: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_available: Mapped[bool] = mapped_column(default=True)
    unavailable_since: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    check_frequency: Mapped[int] = mapped_column(default=24)  # Frequency in hours (6, 12, or 24)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="products")
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")
