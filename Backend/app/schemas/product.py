from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from enum import Enum


class ProductBase(BaseModel):
    url: str
    target_price: float
    check_frequency: Optional[int] = 24  # Default to 24 hours

    @field_validator('check_frequency')
    @classmethod
    def validate_check_frequency(cls, v):
        """Validate that check_frequency is one of the allowed values."""
        if v not in [6, 12, 24]:
            raise ValueError('check_frequency must be 6, 12, or 24 hours')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    target_price: Optional[float] = None
    check_frequency: Optional[int] = None

    @field_validator('check_frequency')
    @classmethod
    def validate_check_frequency(cls, v):
        """Validate that check_frequency is one of the allowed values."""
        if v is not None and v not in [6, 12, 24]:
            raise ValueError('check_frequency must be 6, 12, or 24 hours')
        return v


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
    is_available: bool = True
    unavailable_since: Optional[datetime] = None
    check_frequency: int = 24

    class Config:
        from_attributes = True


class ProductScrapedData(BaseModel):
    name: str
    price: float
    image: Optional[str] = None


class SortOrder(str, Enum):
    """Sort order enum."""

    asc = "asc"
    desc = "desc"


class ProductSortBy(str, Enum):
    """Product sort field enum."""

    name = "name"
    price = "current_price"
    target_price = "target_price"
    created_at = "created_at"
    last_checked = "last_checked"


class PaginationMetadata(BaseModel):
    """Metadata for paginated responses."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedProductsResponse(BaseModel):
    """Paginated response for products."""

    items: List[ProductResponse]
    metadata: PaginationMetadata
