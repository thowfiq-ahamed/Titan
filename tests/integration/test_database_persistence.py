"""
Integration tests for Database Persistence and Session Handling.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from inventory_api.models.item import Item


def test_database_persistence_across_transactions(db_session: Session):
    item = Item(
        sku="TITAN-INT-01",
        name="Integration Test Item",
        category="compute",
        quantity=50,
        price=99.99
    )
    db_session.add(item)
    db_session.commit()

    retrieved = db_session.scalar(select(Item).where(Item.sku == "TITAN-INT-01"))
    assert retrieved is not None
    assert retrieved.name == "Integration Test Item"
    assert retrieved.quantity == 50


def test_database_unique_sku_constraint(db_session: Session):
    item1 = Item(sku="TITAN-UNIQUE-01", name="Item 1", category="general", quantity=1, price=10.0)
    item2 = Item(sku="TITAN-UNIQUE-01", name="Item 2", category="general", quantity=2, price=20.0)

    db_session.add(item1)
    db_session.commit()

    db_session.add(item2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
