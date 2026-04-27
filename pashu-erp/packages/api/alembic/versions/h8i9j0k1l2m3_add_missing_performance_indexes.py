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
    op.create_index("ix_milk_collection_records_center_id", "milk_collection_records", ["center_id"])
    op.create_index("ix_milk_collection_records_farmer_user_id", "milk_collection_records", ["farmer_user_id"])
    op.create_index("ix_health_events_animal_date", "health_events", ["animal_id", "created_at"])
    op.create_index("ix_transactions_category", "transactions", ["category"])


def downgrade() -> None:
    op.drop_index("ix_transactions_category", "transactions")
    op.drop_index("ix_health_events_animal_date", "health_events")
    op.drop_index("ix_milk_collection_records_farmer_user_id", "milk_collection_records")
    op.drop_index("ix_milk_collection_records_center_id", "milk_collection_records")
