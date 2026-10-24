"""
TITAN Inventory API - SQLAlchemy 2.0 Item Data Model
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Numeric, DateTime, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    sku: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="general",
        index=True
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.00
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_items_category_quantity", "category", "quantity"),
    )
