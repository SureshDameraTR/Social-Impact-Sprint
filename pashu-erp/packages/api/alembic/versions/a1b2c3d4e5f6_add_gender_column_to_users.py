"""Add gender column to users table."""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "a1b2c3d4e5f6"
down_revision = "f4a5b6c7d8e9"
branch_labels = None
depends_on = None


def upgrade():
    # Create the gender enum type
    gender_enum = sa.Enum("male", "female", "other", name="gender")
    gender_enum.create(op.get_bind(), checkfirst=True)

    # Add gender column to users table
    op.add_column(
        "users",
        sa.Column("gender", gender_enum, nullable=True),
    )


def downgrade():
    op.drop_column("users", "gender")
    sa.Enum(name="gender").drop(op.get_bind(), checkfirst=True)
