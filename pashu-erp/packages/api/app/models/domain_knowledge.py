from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DiseaseRule(TimestampMixin, Base):
    __tablename__ = "disease_rules"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species_code: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("species_ref.code"),
        nullable=False,
        index=True,
    )
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    symptoms: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False
    )
    min_match: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2
    )
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, server_default="1", nullable=False
    )


class VaccinationScheduleEntry(TimestampMixin, Base):
    __tablename__ = "vaccination_schedule"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species_code: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("species_ref.code"),
        nullable=False,
        index=True,
    )
    vaccine_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    first_dose_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    first_dose_days: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    repeat_interval_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )


class FeedStandard(TimestampMixin, Base):
    __tablename__ = "feed_standards"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    species_code: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("species_ref.code"),
        nullable=False,
        index=True,
    )
    lactation_stage: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    dm_intake_pct_body_weight: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    crude_protein_pct: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    tdn_pct: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
