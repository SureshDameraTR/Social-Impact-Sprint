"""add reference data tables

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-04-09 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c8d9e0f1a2b3'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- market_rates --
    market_rates = op.create_table(
        'market_rates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product', sa.String(length=50), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('min_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('max_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('avg_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('district', sa.String(length=50), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('effective_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('source', sa.String(length=50), server_default=sa.text("'Karnataka APMC'"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- insurance_premiums --
    insurance_premiums = op.create_table(
        'insurance_premiums',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('species', sa.String(length=30), nullable=False),
        sa.Column('breed_type', sa.String(length=30), nullable=False),
        sa.Column('premium_pct', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('animal_value_inr', sa.Integer(), nullable=False),
        sa.Column('scheme_name', sa.String(length=50), server_default=sa.text("'LISS'"), nullable=True),
        sa.Column('effective_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- medicine_catalog --
    op.create_table(
        'medicine_catalog',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('dosage_info', sa.Text(), nullable=True),
        sa.Column('species_applicable', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('withdrawal_period_days', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- Seed market_rates with Karnataka APMC data (13 items) --
    op.bulk_insert(market_rates, [
        {"product": "milk", "unit": "liters", "min_price": 28.0, "max_price": 35.0, "avg_price": 31.5, "district": "Mysore", "label": "Cow Milk"},
        {"product": "eggs", "unit": "pieces", "min_price": 5.0, "max_price": 7.0, "avg_price": 6.0, "district": "Mysore", "label": "Country Eggs"},
        {"product": "goat_milk", "unit": "liters", "min_price": 60.0, "max_price": 80.0, "avg_price": 70.0, "district": "Mysore", "label": "Goat Milk"},
        {"product": "goat_meat", "unit": "kg", "min_price": 600.0, "max_price": 800.0, "avg_price": 700.0, "district": "Mysore", "label": "Goat Meat (live weight)"},
        {"product": "sheep_meat", "unit": "kg", "min_price": 500.0, "max_price": 700.0, "avg_price": 600.0, "district": "Mysore", "label": "Sheep Meat (live weight)"},
        {"product": "wool", "unit": "kg", "min_price": 100.0, "max_price": 150.0, "avg_price": 125.0, "district": "Mysore", "label": "Raw Wool"},
        {"product": "manure", "unit": "kg", "min_price": 2.0, "max_price": 5.0, "avg_price": 3.5, "district": "Mysore", "label": "Organic Manure / Vermicompost"},
        {"product": "buffalo_milk", "unit": "liters", "min_price": 40.0, "max_price": 55.0, "avg_price": 47.5, "district": "Mysore", "label": "Buffalo Milk"},
        {"product": "ghee", "unit": "kg", "min_price": 400.0, "max_price": 600.0, "avg_price": 500.0, "district": "Mysore", "label": "Desi Ghee"},
        {"product": "paneer", "unit": "kg", "min_price": 280.0, "max_price": 350.0, "avg_price": 315.0, "district": "Mysore", "label": "Fresh Paneer"},
        {"product": "curd", "unit": "kg", "min_price": 40.0, "max_price": 60.0, "avg_price": 50.0, "district": "Mysore", "label": "Fresh Curd"},
        {"product": "chicken_broiler", "unit": "kg", "min_price": 150.0, "max_price": 200.0, "avg_price": 175.0, "district": "Mysore", "label": "Broiler Chicken (live)"},
        {"product": "chicken_country", "unit": "kg", "min_price": 350.0, "max_price": 500.0, "avg_price": 425.0, "district": "Mysore", "label": "Country Chicken (live)"},
    ])

    # -- Seed insurance_premiums: 4 species x 3 breed types = 12 rows --
    op.bulk_insert(insurance_premiums, [
        {"species": "cattle", "breed_type": "indigenous", "premium_pct": 3.0, "animal_value_inr": 40000},
        {"species": "cattle", "breed_type": "crossbreed", "premium_pct": 3.5, "animal_value_inr": 60000},
        {"species": "cattle", "breed_type": "exotic", "premium_pct": 4.0, "animal_value_inr": 80000},
        {"species": "goat", "breed_type": "indigenous", "premium_pct": 3.5, "animal_value_inr": 8000},
        {"species": "goat", "breed_type": "crossbreed", "premium_pct": 4.0, "animal_value_inr": 12000},
        {"species": "goat", "breed_type": "exotic", "premium_pct": 4.5, "animal_value_inr": 15000},
        {"species": "sheep", "breed_type": "indigenous", "premium_pct": 3.0, "animal_value_inr": 7000},
        {"species": "sheep", "breed_type": "crossbreed", "premium_pct": 3.5, "animal_value_inr": 10000},
        {"species": "sheep", "breed_type": "exotic", "premium_pct": 4.0, "animal_value_inr": 12000},
        {"species": "poultry", "breed_type": "indigenous", "premium_pct": 5.0, "animal_value_inr": 300},
        {"species": "poultry", "breed_type": "crossbreed", "premium_pct": 5.0, "animal_value_inr": 500},
        {"species": "poultry", "breed_type": "exotic", "premium_pct": 5.0, "animal_value_inr": 800},
    ])


def downgrade() -> None:
    op.drop_table('medicine_catalog')
    op.drop_table('insurance_premiums')
    op.drop_table('market_rates')
