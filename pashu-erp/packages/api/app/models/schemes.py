from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class GovtScheme(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "govt_schemes"
    __table_args__ = (
        CheckConstraint(
            "max_subsidy_amount IS NULL OR max_subsidy_amount > 0",
            name="ck_govt_schemes_subsidy_amount_positive",
        ),
        CheckConstraint(
            "subsidy_percentage IS NULL OR subsidy_percentage BETWEEN 0 AND 100",
            name="ck_govt_schemes_subsidy_pct_range",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    scheme_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    ministry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    eligibility_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    max_subsidy_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    subsidy_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
