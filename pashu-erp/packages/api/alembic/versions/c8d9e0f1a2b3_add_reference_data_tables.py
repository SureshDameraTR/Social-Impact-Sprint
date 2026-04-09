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
    medicine_catalog = op.create_table(
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

    # -- Seed medicine_catalog: 19 common veterinary medicines --
    op.bulk_insert(medicine_catalog, [
        # Antibiotics (5)
        {"name": "Oxytetracycline", "category": "antibiotic", "dosage_info": "5-10 mg/kg bodyweight IM/IV, twice daily for 3-5 days", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 5, "is_active": True},
        {"name": "Enrofloxacin", "category": "antibiotic", "dosage_info": "5 mg/kg bodyweight IM/SC, once daily for 3-5 days", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 7, "is_active": True},
        {"name": "Amoxicillin", "category": "antibiotic", "dosage_info": "7-15 mg/kg bodyweight IM, once daily for 3-5 days", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 5, "is_active": True},
        {"name": "Gentamicin", "category": "antibiotic", "dosage_info": "4-6 mg/kg bodyweight IM/IV, once daily for 5-7 days", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 10, "is_active": True},
        {"name": "Penicillin G", "category": "antibiotic", "dosage_info": "10,000-20,000 IU/kg bodyweight IM, once daily for 3-5 days", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 3, "is_active": True},
        # Anti-parasitic (3)
        {"name": "Ivermectin", "category": "anti_parasitic", "dosage_info": "0.2 mg/kg bodyweight SC, single dose; repeat after 14 days if needed", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 28, "is_active": True},
        {"name": "Albendazole", "category": "anti_parasitic", "dosage_info": "7.5 mg/kg bodyweight oral, single dose", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 7, "is_active": True},
        {"name": "Fenbendazole", "category": "anti_parasitic", "dosage_info": "5-10 mg/kg bodyweight oral, single dose for 3 consecutive days", "species_applicable": "{cattle,goat,sheep}", "withdrawal_period_days": 8, "is_active": True},
        # Anti-inflammatory (2)
        {"name": "Meloxicam", "category": "anti_inflammatory", "dosage_info": "0.5 mg/kg bodyweight SC/IV, single dose; may repeat after 24 hours", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 15, "is_active": True},
        {"name": "Flunixin Meglumine", "category": "anti_inflammatory", "dosage_info": "1.1-2.2 mg/kg bodyweight IV, once daily for up to 3 days", "species_applicable": "{cattle}", "withdrawal_period_days": 4, "is_active": True},
        # Vaccines (6)
        {"name": "FMD Vaccine", "category": "vaccine", "dosage_info": "2 ml SC in neck region; primary at 4 months, booster at 6-month intervals", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "Brucella Vaccine", "category": "vaccine", "dosage_info": "2 ml SC; single dose for female calves at 4-8 months of age", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "HS Vaccine", "category": "vaccine", "dosage_info": "3 ml SC; primary before monsoon, annual booster", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "BQ Vaccine", "category": "vaccine", "dosage_info": "2 ml SC; primary at 6 months, annual booster before monsoon", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "PPR Vaccine", "category": "vaccine", "dosage_info": "1 ml SC; primary at 3 months, booster every 3 years", "species_applicable": "{goat,sheep}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "Enterotoxaemia Vaccine", "category": "vaccine", "dosage_info": "2 ml SC; primary at 4 months, annual booster before monsoon", "species_applicable": "{goat,sheep}", "withdrawal_period_days": 0, "is_active": True},
        # Supplements (3)
        {"name": "Calcium Borogluconate", "category": "supplement", "dosage_info": "250-500 ml of 25% solution IV slow drip; for acute milk fever", "species_applicable": "{cattle,buffalo}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "Iron Dextran", "category": "supplement", "dosage_info": "5-10 ml deep IM; for iron-deficiency anemia in young animals", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 0, "is_active": True},
        {"name": "Vitamin AD3E", "category": "supplement", "dosage_info": "5-10 ml IM; repeat every 2-4 weeks as nutritional supplement", "species_applicable": "{cattle,buffalo,goat,sheep}", "withdrawal_period_days": 0, "is_active": True},
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
