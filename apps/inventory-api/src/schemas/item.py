"""
TITAN Inventory API - Item Schemas
Pydantic v2 data transfer objects with strict validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    sku: str = Field(
        ...,
        min_length=3,
        max_length=64,
        description="Unique Stock Keeping Unit identifier (e.g. TITAN-SRV-01)",
        examples=["TITAN-SRV-01"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Item human-readable name",
        examples=["Rackmount Server 1U"]
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed product or asset description"
    )
    category: str = Field(
        default="general",
        min_length=1,
        max_length=100,
        description="Asset categorization (e.g. compute, storage, networking)",
        examples=["compute"]
    )
    quantity: int = Field(
        default=0,
        ge=0,
        description="Current available stock count (cannot be negative)",
        examples=[10]
    )
    price: float = Field(
        default=0.00,
        ge=0.0,
        description="Unit price (USD)",
        examples=[1299.99]
    )


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    sku: Optional[str] = Field(None, min_length=3, max_length=64)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0.0)


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique UUID of the item")
    created_at: datetime = Field(..., description="Creation timestamp in UTC")
    updated_at: datetime = Field(..., description="Last modification timestamp in UTC")
