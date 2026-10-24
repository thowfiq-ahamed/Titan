"""
Unit tests for Inventory Data Models and Pydantic Schemas.
"""

import pytest
from pydantic import ValidationError
from inventory_api.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from inventory_api.models.item import Item


def test_item_create_valid():
    payload = {
        "sku": "TITAN-NODE-01",
        "name": "Compute Node Alpha",
        "description": "High-density compute blade",
        "category": "compute",
        "quantity": 12,
        "price": 3499.50
    }
    item = ItemCreate(**payload)
    assert item.sku == "TITAN-NODE-01"
    assert item.quantity == 12
    assert item.price == 3499.50


def test_item_create_negative_quantity_fails():
    with pytest.raises(ValidationError):
        ItemCreate(
            sku="TITAN-NODE-02",
            name="Invalid Item",
            quantity=-1,
            price=10.0
        )


def test_item_create_negative_price_fails():
    with pytest.raises(ValidationError):
        ItemCreate(
            sku="TITAN-NODE-03",
            name="Invalid Price",
            quantity=5,
            price=-50.0
        )


def test_item_create_short_sku_fails():
    with pytest.raises(ValidationError):
        ItemCreate(
            sku="AB",  # Min length 3
            name="Invalid SKU",
            quantity=1,
            price=10.0
        )


def test_item_update_partial():
    update_data = {"quantity": 25}
    update_schema = ItemUpdate(**update_data)
    dumped = update_schema.model_dump(exclude_unset=True)
    assert dumped == {"quantity": 25}
    assert "name" not in dumped


def test_sqlalchemy_item_instantiation():
    item = Item(
        sku="TITAN-SW-01",
        name="Top-of-Rack Switch",
        category="networking",
        quantity=4,
        price=4500.00
    )
    assert item.sku == "TITAN-SW-01"
    assert item.category == "networking"
    assert item.quantity == 4
