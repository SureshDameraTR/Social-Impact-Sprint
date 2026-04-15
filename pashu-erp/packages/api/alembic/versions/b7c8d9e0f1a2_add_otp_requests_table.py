"""add otp_requests table

Revision ID: b7c8d9e0f1a2
Revises: g7h8i9j0k1l2
Create Date: 2026-04-09 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'otp_requests',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('phone', sa.String(length=15), nullable=False),
        sa.Column('otp_hash', sa.String(length=128), nullable=False),
        sa.Column('attempts', sa.Integer(), server_default='0', nullable=True),
        sa.Column('request_count', sa.Integer(), server_default='1', nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
    )
    op.create_index('idx_otp_expires', 'otp_requests', ['expires_at'])


def downgrade() -> None:
    op.drop_index('idx_otp_expires', table_name='otp_requests')
    op.drop_table('otp_requests')
