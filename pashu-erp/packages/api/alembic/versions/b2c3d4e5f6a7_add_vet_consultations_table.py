"""Add vet_consultations table."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers
revision = "b2c3d4e5f6a7"
down_revision = "f4a5b6c7d8e9"
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types via raw SQL
    op.execute("CREATE TYPE consultation_status AS ENUM ('pending', 'in_review', 'diagnosed', 'closed')")
    op.execute("CREATE TYPE consultation_priority AS ENUM ('routine', 'urgent', 'emergency')")
    op.execute("CREATE TYPE consultation_channel AS ENUM ('photo', 'walk_in', 'referral')")

    # Reference existing types with create_type=False to prevent double-creation
    consultation_status = postgresql.ENUM(
        "pending", "in_review", "diagnosed", "closed",
        name="consultation_status", create_type=False,
    )
    consultation_priority = postgresql.ENUM(
        "routine", "urgent", "emergency",
        name="consultation_priority", create_type=False,
    )
    consultation_channel = postgresql.ENUM(
        "photo", "walk_in", "referral",
        name="consultation_channel", create_type=False,
    )

    # Create vet_consultations table
    op.create_table(
        "vet_consultations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "animal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("animals.id"),
            nullable=False,
        ),
        sa.Column(
            "farmer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "vet_id",
            postgresql.UUID(as_uuid=True),
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
        sa.Column("photo_urls", postgresql.JSONB, nullable=True),
        sa.Column("diagnosis", sa.Text, nullable=True),
        sa.Column("prescription", sa.Text, nullable=True),
        sa.Column("follow_up_date", sa.Date, nullable=True),
        sa.Column("video_call_url", sa.String(500), nullable=True),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
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
