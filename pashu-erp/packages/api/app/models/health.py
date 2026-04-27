import enum
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class HealthEventType(str, enum.Enum):
    symptom = "symptom"
    checkup = "checkup"
    treatment = "treatment"
    emergency = "emergency"


class HealthEvent(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "health_events"
    __table_args__ = (
        CheckConstraint(
            "ai_risk_score IS NULL OR ai_risk_score BETWEEN 0 AND 1",
            name="ck_health_events_risk_score_range",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        Enum(HealthEventType, name="health_event_type"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    probable_diseases: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships — lazy="noload" to prevent automatic eager loading
    animal = relationship(
        "Animal",
        back_populates="health_events",
        foreign_keys=[animal_id],
        lazy="noload",
    )
    recorder = relationship("User", foreign_keys=[recorded_by], lazy="noload")


class Vaccination(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "vaccinations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True
    )
    vaccine_name: Mapped[str] = mapped_column(String(200), nullable=False)
    administered_on: Mapped[date] = mapped_column(Date, nullable=False)
    next_due: Mapped[date | None] = mapped_column(Date, nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships — lazy="noload" to prevent automatic eager loading
    animal = relationship(
        "Animal",
        back_populates="vaccinations",
        foreign_keys=[animal_id],
        lazy="noload",
    )
    recorder = relationship("User", foreign_keys=[recorded_by], lazy="noload")
