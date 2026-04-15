"""add composite indexes for soft-delete query patterns

Revision ID: c0mp051t31dx
Revises: b2c3d4e5f6a7
Create Date: 2026-04-15 12:00:00.000000

Add composite (user_id, deleted_at) and (animal_id, deleted_at) indexes
to accelerate the most common filtered queries on soft-deleted tables.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "c0mp051t31dx"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # (user_id, deleted_at) composite indexes
    op.create_index(
        "ix_animals_user_id_deleted_at",
        "animals",
        ["user_id", "deleted_at"],
    )
    op.create_index(
        "ix_health_events_animal_id_deleted_at",
        "health_events",
        ["animal_id", "deleted_at"],
    )
    op.create_index(
        "ix_yield_logs_user_id_deleted_at",
        "yield_logs",
        ["user_id", "deleted_at"],
    )
    op.create_index(
        "ix_transactions_user_id_deleted_at",
        "transactions",
        ["user_id", "deleted_at"],
    )
    op.create_index(
        "ix_sell_records_user_id_deleted_at",
        "sell_records",
        ["user_id", "deleted_at"],
    )

    # (animal_id, deleted_at) composite indexes
    op.create_index(
        "ix_yield_logs_animal_id_deleted_at",
        "yield_logs",
        ["animal_id", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_yield_logs_animal_id_deleted_at", "yield_logs")
    op.drop_index("ix_sell_records_user_id_deleted_at", "sell_records")
    op.drop_index("ix_transactions_user_id_deleted_at", "transactions")
    op.drop_index("ix_yield_logs_user_id_deleted_at", "yield_logs")
    op.drop_index("ix_health_events_animal_id_deleted_at", "health_events")
    op.drop_index("ix_animals_user_id_deleted_at", "animals")
