"""add reference data system tables

Revision ID: r3f3r3nc3d4t4
Revises: h8i9j0k1l2m3
Create Date: 2026-04-27 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "r3f3r3nc3d4t4"
down_revision: Union[str, None] = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- states --
    op.create_table(
        "states",
        sa.Column("lgd_code", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_local", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("lgd_code"),
        sa.UniqueConstraint("name"),
    )

    # -- districts --
    op.create_table(
        "districts",
        sa.Column("lgd_code", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_local", sa.String(length=100), nullable=True),
        sa.Column("state_lgd_code", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("elevation_m", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["state_lgd_code"], ["states.lgd_code"]),
        sa.PrimaryKeyConstraint("lgd_code"),
    )
    op.create_index("ix_districts_state_lgd_code", "districts", ["state_lgd_code"])

    # -- sub_districts --
    op.create_table(
        "sub_districts",
        sa.Column("lgd_code", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_local", sa.String(length=100), nullable=True),
        sa.Column("district_lgd_code", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["district_lgd_code"], ["districts.lgd_code"]),
        sa.PrimaryKeyConstraint("lgd_code"),
    )
    op.create_index("ix_sub_districts_district_lgd_code", "sub_districts", ["district_lgd_code"])

    # -- villages --
    op.create_table(
        "villages",
        sa.Column("lgd_code", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_local", sa.String(length=200), nullable=True),
        sa.Column("sub_district_lgd_code", sa.Integer(), nullable=False),
        sa.Column("pincode", sa.String(length=6), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sub_district_lgd_code"], ["sub_districts.lgd_code"]),
        sa.PrimaryKeyConstraint("lgd_code"),
    )
    op.create_index("ix_villages_sub_district_lgd_code", "villages", ["sub_district_lgd_code"])
    op.create_index("ix_villages_sub_district_name", "villages", ["sub_district_lgd_code", "name"])

    # -- species_ref --
    op.create_table(
        "species_ref",
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name_en", sa.String(length=50), nullable=False),
        sa.Column("name_kn", sa.String(length=50), nullable=True),
        sa.Column("name_hi", sa.String(length=50), nullable=True),
        sa.Column("emoji", sa.String(length=10), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )

    # -- breeds --
    op.create_table(
        "breeds",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_local", sa.String(length=100), nullable=True),
        sa.Column("species_code", sa.String(length=30), nullable=False),
        sa.Column("origin", sa.String(length=100), nullable=True),
        sa.Column("nbagr_code", sa.String(length=50), nullable=True),
        sa.Column("is_indigenous", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["species_code"], ["species_ref.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_breeds_species_code", "breeds", ["species_code"])

    # -- disease_rules --
    op.create_table(
        "disease_rules",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("species_code", sa.String(length=30), nullable=False),
        sa.Column("disease_name", sa.String(length=200), nullable=False),
        sa.Column("symptoms", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("min_match", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["species_code"], ["species_ref.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_disease_rules_species_code", "disease_rules", ["species_code"])

    # -- vaccination_schedule --
    op.create_table(
        "vaccination_schedule",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("species_code", sa.String(length=30), nullable=False),
        sa.Column("vaccine_name", sa.String(length=100), nullable=False),
        sa.Column("first_dose_months", sa.Integer(), nullable=True),
        sa.Column("first_dose_days", sa.Integer(), nullable=True),
        sa.Column("repeat_interval_months", sa.Integer(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["species_code"], ["species_ref.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vaccination_schedule_species_code", "vaccination_schedule", ["species_code"])

    # -- feed_standards --
    op.create_table(
        "feed_standards",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("species_code", sa.String(length=30), nullable=False),
        sa.Column("lactation_stage", sa.String(length=20), nullable=True),
        sa.Column("dm_intake_pct_body_weight", sa.Numeric(8, 4), nullable=False),
        sa.Column("crude_protein_pct", sa.Numeric(8, 4), nullable=False),
        sa.Column("tdn_pct", sa.Numeric(8, 4), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["species_code"], ["species_ref.code"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feed_standards_species_code", "feed_standards", ["species_code"])


def downgrade() -> None:
    op.drop_table("feed_standards")
    op.drop_table("vaccination_schedule")
    op.drop_table("disease_rules")
    op.drop_table("breeds")
    op.drop_table("species_ref")
    op.drop_table("villages")
    op.drop_table("sub_districts")
    op.drop_table("districts")
    op.drop_table("states")
