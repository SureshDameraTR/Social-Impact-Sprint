"""add FK ON DELETE RESTRICT, yield_logs unique constraint, and updated_at columns

Revision ID: d4e5f6a7b8c9
Revises: c0mp051t31dx
Create Date: 2026-04-15 14:00:00.000000

Addresses audit findings:
  DATA-04: No ON DELETE clause on any foreign key
  DATA-06: No unique constraint on yield_logs to prevent duplicate milk recordings
  DATA-10: Models don't use TimestampMixin, so most tables lack updated_at
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c0mp051t31dx"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tables that currently lack an updated_at column.
_TABLES_NEEDING_UPDATED_AT = [
    "animals",
    "health_events",
    "vaccinations",
    "yield_logs",
    "milk_collection_centers",
    "milk_collection_records",
    "transactions",
    "sell_records",
    "insurance_policies",
    "insurance_claims",
    "advisory_tips",
    "feed_ingredients",
    "medicines",
    "medicine_administrations",
    "shg_groups",
    "govt_schemes",
    "community_alerts",
    "traditional_remedies",
    "weather_alerts",
    "otp_requests",
]

# Foreign key constraints to add ON DELETE RESTRICT.
# Each tuple: (constraint_name, source_table, source_col, ref_table, ref_col)
_FK_CONSTRAINTS = [
    ("fk_animals_user_id_users", "animals", "user_id", "users", "id"),
    ("fk_health_events_animal_id_animals", "health_events", "animal_id", "animals", "id"),
    ("fk_vaccinations_animal_id_animals", "vaccinations", "animal_id", "animals", "id"),
    ("fk_yield_logs_animal_id_animals", "yield_logs", "animal_id", "animals", "id"),
    ("fk_yield_logs_user_id_users", "yield_logs", "user_id", "users", "id"),
]


def upgrade() -> None:
    # --- A) Add updated_at to tables that lack it ---
    for table in _TABLES_NEEDING_UPDATED_AT:
        op.add_column(
            table,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
        )

    # --- B) Add unique constraint on yield_logs ---
    op.create_unique_constraint(
        "uq_yield_logs_animal_session_date",
        "yield_logs",
        ["animal_id", "session", "recorded_at"],
    )

    # --- C) Replace bare FKs with ON DELETE RESTRICT ---
    for fk_name, src_table, src_col, ref_table, ref_col in _FK_CONSTRAINTS:
        # Drop the existing unnamed/auto-named FK constraint.
        # SQLAlchemy auto-generates names like "<table>_<col>_fkey".
        op.drop_constraint(
            f"{src_table}_{src_col}_fkey",
            src_table,
            type_="foreignkey",
        )
        # Re-create with ON DELETE RESTRICT.
        op.create_foreign_key(
            fk_name,
            src_table,
            ref_table,
            [src_col],
            [ref_col],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    # --- C) Revert FK constraints back to bare (no ON DELETE clause) ---
    for fk_name, src_table, src_col, ref_table, ref_col in reversed(_FK_CONSTRAINTS):
        op.drop_constraint(fk_name, src_table, type_="foreignkey")
        op.create_foreign_key(
            f"{src_table}_{src_col}_fkey",
            src_table,
            ref_table,
            [src_col],
            [ref_col],
        )

    # --- B) Drop unique constraint on yield_logs ---
    op.drop_constraint(
        "uq_yield_logs_animal_session_date",
        "yield_logs",
        type_="unique",
    )

    # --- A) Drop updated_at from all tables ---
    for table in reversed(_TABLES_NEEDING_UPDATED_AT):
        op.drop_column(table, "updated_at")
