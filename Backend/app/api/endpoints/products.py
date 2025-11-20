from datetime import datetime
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.base import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.price_history import PriceHistoryResponse, PriceHistoryStats
from app.schemas.product import (
    PaginatedProductsResponse,
    PaginationMetadata,
    ProductCreate,
    ProductResponse,
    ProductSortBy,
    ProductUpdate,
    SortOrder,
)
from app.services.email import email_service
from app.services.price_history import price_history_service
from app.services.scraper import scraper

router = APIRouter()


@router.get("", response_model=PaginatedProductsResponse)
def get_products(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by product name or URL"),
    sort_by: ProductSortBy = Query(ProductSortBy.created_at, description="Field to sort by"),
    order: SortOrder = Query(SortOrder.desc, description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated products tracked by the current user.

    Supports:
    - Pagination (page, page_size)
    - Searching (by name or URL)
    - Sorting (by name, price, target_price, created_at, last_checked)
    - Ordering (ascending or descending)
    """
    # Base query
    query = db.query(Product).filter(Product.user_id == current_user.id)

    # Apply search filter
    if search:
        search_filter = or_(
            func.lower(Product.name).contains(func.lower(search)), func.lower(Product.url).contains(func.lower(search))
        )
        query = query.filter(search_filter)

    # Get total count before pagination
    total_items = query.count()

    # Apply sorting
    sort_column = getattr(Product, sort_by.value)
    if order == SortOrder.asc:
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    products = query.offset(offset).limit(page_size).all()

    # Calculate metadata
    total_pages = ceil(total_items / page_size) if total_items > 0 else 1

    metadata = PaginationMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )

    # Convert ORM models to Pydantic response models
    product_responses = [ProductResponse.model_validate(p) for p in products]

    return PaginatedProductsResponse(items=product_responses, metadata=metadata)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Add a new product to track."""
    # Scrape product information
    scraped_data = scraper.scrape_product(product_data.url)

    if not scraped_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to extract product information from URL. Please check the URL and try again.",
        )

    # Create new product
    new_product = Product(
        user_id=current_user.id,
        name=scraped_data.name,
        url=product_data.url,
        image=scraped_data.image,
        current_price=scraped_data.price,
        target_price=product_data.target_price,
        last_checked=datetime.utcnow(),
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Record initial price in history
    price_history_service.record_price(db, new_product.id, scraped_data.price)

    return new_product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a product (name or target price)."""
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.target_price is not None:
        product.target_price = product_data.target_price

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a product from tracking."""
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()

    return None


@router.post("/{product_id}/check", response_model=ProductResponse)
def check_product_price(
    product_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually check and update the price of a product."""
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Scrape current price
    scraped_data = scraper.scrape_product(product.url)

    if not scraped_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to fetch current price")

    old_price = product.current_price
    product.current_price = scraped_data.price
    product.last_checked = datetime.utcnow()

    # Record price in history if it has changed
    if price_history_service.should_record_price(db, product.id, scraped_data.price):
        price_history_service.record_price(db, product.id, scraped_data.price)

    # Check if price dropped below target
    if scraped_data.price <= product.target_price and old_price > product.target_price:
        # Send email notification in background
        background_tasks.add_task(
            email_service.send_price_alert, current_user.email, product.name, scraped_data.price, old_price, product.url
        )

    db.commit()
    db.refresh(product)

    return product


@router.get("/{product_id}/history", response_model=List[PriceHistoryResponse])
def get_product_price_history(
    product_id: int, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get the price history for a specific product.

    Args:
        product_id: ID of the product
        limit: Maximum number of history records to return (default: 100)

    Returns:
        List of price history records, ordered by date (newest first)
    """
    # Verify product belongs to current user
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Get price history
    history = price_history_service.get_product_history(db, product_id, limit)

    return history


@router.get("/{product_id}/history/stats", response_model=PriceHistoryStats)
def get_product_price_statistics(
    product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get price statistics for a specific product.

    Args:
        product_id: ID of the product

    Returns:
        Price statistics including lowest, highest, average, and change percentage
    """
    # Verify product belongs to current user
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Get statistics
    stats = price_history_service.get_price_statistics(db, product_id)

    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return stats
