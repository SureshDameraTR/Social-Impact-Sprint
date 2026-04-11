"""float to numeric financial columns

Revision ID: e3f4a5b6c7d8
Revises: c8d9e0f1a2b3
Create Date: 2026-04-11 12:00:00.000000

Fix CRIT-5 (Financial Float->Decimal) and MED-9 (Float/Numeric inconsistency).
Convert all financial and quantity columns from DOUBLE PRECISION to NUMERIC
to prevent cumulative rounding errors in settlements.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, None] = 'c8d9e0f1a2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # yield_logs
    op.alter_column('yield_logs', 'quantity_liters',
                     type_=sa.Numeric(precision=12, scale=2),
                     existing_type=sa.Float())

    # milk_collection_records
    op.alter_column('milk_collection_records', 'quantity_liters',
                     type_=sa.Numeric(precision=12, scale=2),
                     existing_type=sa.Float())
    op.alter_column('milk_collection_records', 'fat_pct',
                     type_=sa.Numeric(precision=5, scale=2),
                     existing_type=sa.Float())
    op.alter_column('milk_collection_records', 'snf_pct',
                     type_=sa.Numeric(precision=5, scale=2),
                     existing_type=sa.Float())
    op.alter_column('milk_collection_records', 'rate_per_liter',
                     type_=sa.Numeric(precision=10, scale=2),
                     existing_type=sa.Float())
    op.alter_column('milk_collection_records', 'total_amount',
                     type_=sa.Numeric(precision=10, scale=2),
                     existing_type=sa.Float())

    # sell_records
    op.alter_column('sell_records', 'quantity',
                     type_=sa.Numeric(precision=12, scale=2),
                     existing_type=sa.Float())

    # feed_ingredients
    op.alter_column('feed_ingredients', 'protein_pct',
                     type_=sa.Numeric(precision=5, scale=2),
                     existing_type=sa.Float())
    op.alter_column('feed_ingredients', 'energy_kcal',
                     type_=sa.Numeric(precision=10, scale=2),
                     existing_type=sa.Float())

    # govt_schemes
    op.alter_column('govt_schemes', 'subsidy_percentage',
                     type_=sa.Numeric(precision=5, scale=2),
                     existing_type=sa.Float())

    # animals
    op.alter_column('animals', 'body_condition_score',
                     type_=sa.Numeric(precision=3, scale=1),
                     existing_type=sa.Float())

    # health_events
    op.alter_column('health_events', 'ai_risk_score',
                     type_=sa.Numeric(precision=5, scale=2),
                     existing_type=sa.Float())


def downgrade() -> None:
    # Revert all columns back to Float (double precision)
    op.alter_column('yield_logs', 'quantity_liters',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=12, scale=2))

    op.alter_column('milk_collection_records', 'quantity_liters',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=12, scale=2))
    op.alter_column('milk_collection_records', 'fat_pct',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=5, scale=2))
    op.alter_column('milk_collection_records', 'snf_pct',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=5, scale=2))
    op.alter_column('milk_collection_records', 'rate_per_liter',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=10, scale=2))
    op.alter_column('milk_collection_records', 'total_amount',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=10, scale=2))

    op.alter_column('sell_records', 'quantity',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=12, scale=2))

    op.alter_column('feed_ingredients', 'protein_pct',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=5, scale=2))
    op.alter_column('feed_ingredients', 'energy_kcal',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=10, scale=2))

    op.alter_column('govt_schemes', 'subsidy_percentage',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=5, scale=2))

    op.alter_column('animals', 'body_condition_score',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=3, scale=1))

    op.alter_column('health_events', 'ai_risk_score',
                     type_=sa.Float(),
                     existing_type=sa.Numeric(precision=5, scale=2))
