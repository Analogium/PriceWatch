from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    url: str
    target_price: float


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    target_price: Optional[float] = None


class ProductResponse(BaseModel):
    id: int
    user_id: int
    name: str
    url: str
    image: Optional[str]
    current_price: float
    target_price: float
    last_checked: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ProductScrapedData(BaseModel):
    name: str
    price: float
    image: Optional[str] = None
