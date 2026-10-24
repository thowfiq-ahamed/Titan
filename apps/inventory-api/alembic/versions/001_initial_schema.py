"""Initial items schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-24 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_sku'), 'items', ['sku'], unique=True)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    op.create_index(op.f('ix_items_category'), 'items', ['category'], unique=False)
    op.create_index('idx_items_category_quantity', 'items', ['category', 'quantity'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_items_category_quantity', table_name='items')
    op.drop_index(op.f('ix_items_category'), table_name='items')
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_sku'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')
