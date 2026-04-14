"""Add audit columns (created_by, updated_by), soft delete (deleted_at), and aadhaar_hash unique constraint."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = "f4a5b6c7d8e9"
down_revision = "e3f4a5b6c7d8"
branch_labels = None
depends_on = None

# All tables that get the audit + soft-delete columns
TABLES = [
    "users",
    "animals",
    "health_events",
    "vaccinations",
    "yield_logs",
    "milk_collection_centers",
    "milk_collection_records",
    "transactions",
    "sell_records",
    "govt_schemes",
    "advisory_tips",
    "community_alerts",
    "traditional_remedies",
    "feed_ingredients",
    "insurance_policies",
    "insurance_claims",
    "medicines",
    "medicine_administrations",
    "market_rates",
    "insurance_premiums",
    "medicine_catalog",
    "shg_groups",
    "weather_alerts",
]


def upgrade():
    # 1. Add audit columns (created_by, updated_by) to all business tables
    for table in TABLES:
        op.add_column(table, sa.Column("created_by", UUID(as_uuid=True), nullable=True))
        op.add_column(table, sa.Column("updated_by", UUID(as_uuid=True), nullable=True))
        op.create_index(f"ix_{table}_created_by", table, ["created_by"])

    # 2. Add soft-delete column (deleted_at) to all business tables
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])

    # 3. Add unique constraint on aadhaar_hash (users table)
    op.create_unique_constraint("uq_users_aadhaar_hash", "users", ["aadhaar_hash"])


def downgrade():
    # Remove unique constraint
    op.drop_constraint("uq_users_aadhaar_hash", "users", type_="unique")

    # Remove soft-delete and audit columns
    for table in reversed(TABLES):
        op.drop_index(f"ix_{table}_deleted_at", table)
        op.drop_column(table, "deleted_at")
        op.drop_index(f"ix_{table}_created_by", table)
        op.drop_column(table, "updated_by")
        op.drop_column(table, "created_by")
