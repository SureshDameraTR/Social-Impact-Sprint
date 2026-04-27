"""Reference data models -- market rates, insurance premiums, medicine catalog."""

from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class MarketRate(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "market_rates"
    __table_args__ = (
        CheckConstraint("min_price >= 0", name="ck_market_rates_min_price_non_negative"),
        CheckConstraint("max_price >= 0", name="ck_market_rates_max_price_non_negative"),
        CheckConstraint("avg_price >= 0", name="ck_market_rates_avg_price_non_negative"),
        CheckConstraint("min_price <= max_price", name="ck_market_rates_min_lte_max"),
    )

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
    source: Mapped[str] = mapped_column(
        String(50), default="Karnataka APMC", server_default=text("'Karnataka APMC'")
    )


class InsurancePremium(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "insurance_premiums"
    __table_args__ = (
        CheckConstraint(
            "premium_pct BETWEEN 0 AND 100", name="ck_insurance_premiums_pct_range"
        ),
        CheckConstraint("animal_value_inr > 0", name="ck_insurance_premiums_value_positive"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species: Mapped[str] = mapped_column(String(30), nullable=False)
    breed_type: Mapped[str] = mapped_column(String(30), nullable=False)
    premium_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    animal_value_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    scheme_name: Mapped[str] = mapped_column(
        String(50), default="LISS", server_default=text("'LISS'")
    )
    effective_date: Mapped[date] = mapped_column(Date, server_default=text("CURRENT_DATE"))


class MedicineCatalog(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
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
    withdrawal_period_days: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
