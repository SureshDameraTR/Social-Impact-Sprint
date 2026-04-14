from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditMixin:
    """Adds created_by / updated_by UUID columns referencing users.id."""

    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True,
    )
    updated_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )


class SoftDeleteMixin:
    """Adds deleted_at timestamp for soft-delete support."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, index=True,
    )
