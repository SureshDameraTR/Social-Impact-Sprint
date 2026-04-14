"""Add vet_consultations table."""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    consultation_status = sa.Enum(
        "pending", "in_review", "diagnosed", "closed", name="consultation_status"
    )
    consultation_status.create(op.get_bind(), checkfirst=True)

    consultation_priority = sa.Enum(
        "routine", "urgent", "emergency", name="consultation_priority"
    )
    consultation_priority.create(op.get_bind(), checkfirst=True)

    consultation_channel = sa.Enum(
        "photo", "walk_in", "referral", name="consultation_channel"
    )
    consultation_channel.create(op.get_bind(), checkfirst=True)

    # Create vet_consultations table
    op.create_table(
        "vet_consultations",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "animal_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("animals.id"),
            nullable=False,
        ),
        sa.Column(
            "farmer_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "vet_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "status", consultation_status, nullable=False, server_default="pending"
        ),
        sa.Column(
            "priority", consultation_priority, nullable=False, server_default="routine"
        ),
        sa.Column("channel", consultation_channel, nullable=False),
        sa.Column("farmer_notes", sa.Text, nullable=True),
        sa.Column("photo_urls", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("diagnosis", sa.Text, nullable=True),
        sa.Column("prescription", sa.Text, nullable=True),
        sa.Column("follow_up_date", sa.Date, nullable=True),
        sa.Column("video_call_url", sa.String(500), nullable=True),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column(
            "created_by",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.dialects.postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes
    op.create_index("ix_vet_consultations_district", "vet_consultations", ["district"])
    op.create_index("ix_vet_consultations_status", "vet_consultations", ["status"])
    op.create_index(
        "ix_vet_consultations_farmer_id", "vet_consultations", ["farmer_id"]
    )
    op.create_index("ix_vet_consultations_vet_id", "vet_consultations", ["vet_id"])


def downgrade():
    op.drop_table("vet_consultations")
    sa.Enum(name="consultation_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="consultation_priority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="consultation_channel").drop(op.get_bind(), checkfirst=True)
