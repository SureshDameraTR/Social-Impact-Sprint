"""Add missing performance indexes for milk_collection_records, health_events, transactions.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-04-20 13:00:00.000000
"""
from alembic import op

revision = "h8i9j0k1l2m3"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ix_health_events_animal_date already created in a1b2c3d4e5f6
    # ix_milk_collection_center_id and ix_milk_collection_farmer already created in a1b2c3d4e5f6
    op.create_index("ix_transactions_category", "transactions", ["category"])


def downgrade() -> None:
    op.drop_index("ix_transactions_category", "transactions")
