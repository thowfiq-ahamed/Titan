"""
TITAN Inventory API - Item CRUD Router
Implements REST endpoints for managing inventory assets.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.item import Item
from ..schemas.item import ItemCreate, ItemUpdate, ItemResponse
from ..schemas.common import PaginatedResponse
from ..logging import logger
from ..metrics import INVENTORY_ITEMS_TOTAL, DATABASE_ERRORS_TOTAL

router = APIRouter(prefix="/items", tags=["Inventory Items"])


@router.get(
    "",
    response_model=PaginatedResponse[ItemResponse],
    summary="List Inventory Items",
    description="Retrieve a paginated list of inventory items with optional category filtering and keyword search."
)
def list_items(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search term matching SKU or Name"),
    db: Session = Depends(get_db)
) -> PaginatedResponse[ItemResponse]:
    try:
        query = select(Item)
        count_query = select(func.count(Item.id))

        if category:
            query = query.where(Item.category == category)
            count_query = count_query.where(Item.category == category)

        if search:
            search_filter = or_(
                Item.sku.ilike(f"%{search}%"),
                Item.name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = db.scalar(count_query) or 0
        items = db.scalars(query.order_by(Item.created_at.desc()).offset(skip).limit(limit)).all()

        # Update metrics gauge with overall item count
        total_items_in_db = db.scalar(select(func.count(Item.id))) or 0
        INVENTORY_ITEMS_TOTAL.set(total_items_in_db)

        return PaginatedResponse(
            items=[ItemResponse.model_validate(item) for item in items],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as exc:
        DATABASE_ERRORS_TOTAL.labels(operation="list_items").inc()
        logger.error(f"Error listing inventory items: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query inventory records"
        )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get Item Details",
    description="Fetch a specific inventory item by its unique UUID."
)
def get_item(item_id: str, db: Session = Depends(get_db)) -> ItemResponse:
    item = db.scalar(select(Item).where(Item.id == item_id))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found"
        )
    return ItemResponse.model_validate(item)


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Inventory Item",
    description="Register a new inventory item with a unique SKU identifier."
)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemResponse:
    # Check for existing SKU
    existing = db.scalar(select(Item).where(Item.sku == payload.sku))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with SKU '{payload.sku}' already exists"
        )

    try:
        new_item = Item(
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            category=payload.category,
            quantity=payload.quantity,
            price=payload.price
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        total_items = db.scalar(select(func.count(Item.id))) or 0
        INVENTORY_ITEMS_TOTAL.set(total_items)

        logger.info(f"Created inventory item: sku={new_item.sku}, id={new_item.id}")
        return ItemResponse.model_validate(new_item)
    except Exception as exc:
        db.rollback()
        DATABASE_ERRORS_TOTAL.labels(operation="create_item").inc()
        logger.error(f"Failed to create inventory item {payload.sku}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist inventory item"
        )


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update Inventory Item",
    description="Update fields on an existing inventory item."
)
def update_item(item_id: str, payload: ItemUpdate, db: Session = Depends(get_db)) -> ItemResponse:
    item = db.scalar(select(Item).where(Item.id == item_id))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found"
        )

    # If updating SKU, check for collision
    if payload.sku and payload.sku != item.sku:
        existing = db.scalar(select(Item).where(Item.sku == payload.sku))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot update SKU: '{payload.sku}' is already in use by another item"
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    try:
        db.commit()
        db.refresh(item)
        logger.info(f"Updated inventory item id={item.id}, sku={item.sku}")
        return ItemResponse.model_validate(item)
    except Exception as exc:
        db.rollback()
        DATABASE_ERRORS_TOTAL.labels(operation="update_item").inc()
        logger.error(f"Failed to update item {item_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update inventory record"
        )


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Inventory Item",
    description="Remove an item from the inventory catalog."
)
def delete_item(item_id: str, db: Session = Depends(get_db)) -> None:
    item = db.scalar(select(Item).where(Item.id == item_id))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID '{item_id}' not found"
        )

    try:
        db.delete(item)
        db.commit()

        total_items = db.scalar(select(func.count(Item.id))) or 0
        INVENTORY_ITEMS_TOTAL.set(total_items)

        logger.info(f"Deleted inventory item id={item_id}")
        return None
    except Exception as exc:
        db.rollback()
        DATABASE_ERRORS_TOTAL.labels(operation="delete_item").inc()
        logger.error(f"Failed to delete item {item_id}: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete inventory item"
        )
