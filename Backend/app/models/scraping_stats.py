from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScrapingStats(Base):
    __tablename__ = "scraping_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    site_name: Mapped[str] = mapped_column(String, index=True)  # amazon, fnac, darty, etc.
    product_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # Optional reference to product
    status: Mapped[str] = mapped_column(String)  # success, failure, unavailable
    response_time: Mapped[Optional[float]] = mapped_column(nullable=True)  # Time taken to scrape in seconds
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
