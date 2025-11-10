from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PriceHistoryBase(BaseModel):
    """Base schema for PriceHistory"""
    price: float = Field(..., description="Prix enregistré")


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating a price history entry"""
    product_id: int = Field(..., description="ID du produit")


class PriceHistoryResponse(PriceHistoryBase):
    """Schema for price history response"""
    id: int
    product_id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class PriceHistoryStats(BaseModel):
    """Schema for price history statistics"""
    current_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    price_change_percentage: Optional[float] = None
    total_records: int

    class Config:
        from_attributes = True
