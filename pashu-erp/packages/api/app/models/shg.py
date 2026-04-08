import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Boolean, Date, DateTime, Numeric, Enum, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SHGGrading(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    ungraded = "ungraded"


class SHGGroup(Base):
    __tablename__ = "shg_groups"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    registration_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    admin_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    member_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    women_only: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    formation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_savings: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0"
    )
    grading: Mapped[str] = mapped_column(
        Enum(SHGGrading, name="shg_grading"),
        default=SHGGrading.ungraded,
        server_default="ungraded",
    )
    panchsutra_compliance: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship("User", foreign_keys=[admin_user_id])
