from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from datetime import datetime
from app.db.base import Base


class ScrapingStats(Base):
    __tablename__ = "scraping_stats"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, nullable=False, index=True)  # amazon, fnac, darty, etc.
    product_id = Column(Integer, nullable=True)  # Optional reference to product
    status = Column(String, nullable=False)  # success, failure, unavailable
    response_time = Column(Float, nullable=True)  # Time taken to scrape in seconds
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
