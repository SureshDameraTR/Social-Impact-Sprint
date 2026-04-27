"""Add buffalo to species enum."""

from typing import Union

from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: str | None = "e5f6a7b8c9d0"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade():
    op.execute("ALTER TYPE species ADD VALUE IF NOT EXISTS 'buffalo' AFTER 'cattle'")


def downgrade():
    # PostgreSQL does not support removing values from enums.
    # A full enum replacement would be needed; left as no-op for safety.
    pass
