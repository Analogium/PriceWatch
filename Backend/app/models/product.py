from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image = Column(String, nullable=True)
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_available = Column(Boolean, default=True, nullable=False)
    unavailable_since = Column(DateTime, nullable=True)
    check_frequency = Column(Integer, default=24, nullable=False)  # Frequency in hours (6, 12, or 24)

    # Relationships
    owner = relationship("User", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
