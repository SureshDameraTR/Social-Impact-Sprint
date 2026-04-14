"""Reference data models -- market rates, insurance premiums, medicine catalog."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class MarketRate(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "market_rates"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    product: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    min_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    avg_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    source: Mapped[str] = mapped_column(String(50), default="Karnataka APMC", server_default=text("'Karnataka APMC'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InsurancePremium(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "insurance_premiums"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species: Mapped[str] = mapped_column(String(30), nullable=False)
    breed_type: Mapped[str] = mapped_column(String(30), nullable=False)
    premium_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    animal_value_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(50), default="LISS", server_default=text("'LISS'"))
    effective_date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MedicineCatalog(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "medicine_catalog"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    dosage_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    species_applicable: Mapped[list | None] = mapped_column(ARRAY(String), nullable=True)
    withdrawal_period_days: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
