"""Add performance indexes on FK and time columns."""

from alembic import op

# revision identifiers
revision = "a1b2c3d4e5f6"
down_revision = "d22bbd14c60e"
branch_labels = None
depends_on = None


def upgrade():
    # Foreign key indexes
    op.create_index("ix_animals_user_id", "animals", ["user_id"])
    op.create_index("ix_health_events_animal_id", "health_events", ["animal_id"])
    op.create_index("ix_health_events_event_date", "health_events", ["event_date"])
    op.create_index("ix_vaccinations_animal_id", "vaccinations", ["animal_id"])
    op.create_index("ix_yield_logs_user_id", "yield_logs", ["user_id"])
    op.create_index("ix_yield_logs_animal_id", "yield_logs", ["animal_id"])
    op.create_index("ix_yield_logs_recorded_at", "yield_logs", ["recorded_at"])
    op.create_index("ix_milk_collection_center_id", "milk_collection_records", ["center_id"])
    op.create_index("ix_milk_collection_farmer", "milk_collection_records", ["farmer_user_id"])
    op.create_index("ix_sell_records_user_id", "sell_records", ["user_id"])
    op.create_index("ix_sell_records_sold_at", "sell_records", ["sold_at"])
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_index("ix_medicine_admin_animal_id", "medicine_administrations", ["animal_id"])
    op.create_index("ix_insurance_policies_animal_id", "insurance_policies", ["animal_id"])
    # Composite indexes for common query patterns
    op.create_index("ix_animals_user_created", "animals", ["user_id", "created_at"])
    op.create_index("ix_health_events_animal_date", "health_events", ["animal_id", "event_date"])
    op.create_index("ix_yield_logs_user_recorded", "yield_logs", ["user_id", "recorded_at"])
    op.create_index("ix_milk_collection_center_date", "milk_collection_records", ["center_id", "collected_at"])


def downgrade():
    op.drop_index("ix_milk_collection_center_date", "milk_collection_records")
    op.drop_index("ix_yield_logs_user_recorded", "yield_logs")
    op.drop_index("ix_health_events_animal_date", "health_events")
    op.drop_index("ix_animals_user_created", "animals")
    op.drop_index("ix_insurance_policies_animal_id", "insurance_policies")
    op.drop_index("ix_medicine_admin_animal_id", "medicine_administrations")
    op.drop_index("ix_transactions_created_at", "transactions")
    op.drop_index("ix_transactions_user_id", "transactions")
    op.drop_index("ix_sell_records_sold_at", "sell_records")
    op.drop_index("ix_sell_records_user_id", "sell_records")
    op.drop_index("ix_milk_collection_farmer", "milk_collection_records")
    op.drop_index("ix_milk_collection_center_id", "milk_collection_records")
    op.drop_index("ix_yield_logs_recorded_at", "yield_logs")
    op.drop_index("ix_yield_logs_animal_id", "yield_logs")
    op.drop_index("ix_yield_logs_user_id", "yield_logs")
    op.drop_index("ix_vaccinations_animal_id", "vaccinations")
    op.drop_index("ix_health_events_event_date", "health_events")
    op.drop_index("ix_health_events_animal_id", "health_events")
    op.drop_index("ix_animals_user_id", "animals")
