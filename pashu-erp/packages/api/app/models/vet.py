import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class ConsultationStatus(str, enum.Enum):
    pending = "pending"
    in_review = "in_review"
    diagnosed = "diagnosed"
    closed = "closed"


class ConsultationPriority(str, enum.Enum):
    routine = "routine"
    urgent = "urgent"
    emergency = "emergency"


class ConsultationChannel(str, enum.Enum):
    photo = "photo"
    walk_in = "walk_in"
    referral = "referral"


class VetConsultation(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "vet_consultations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True
    )
    farmer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    vet_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum(ConsultationStatus, name="consultation_status"),
        nullable=False,
        server_default="pending",
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        Enum(ConsultationPriority, name="consultation_priority"),
        nullable=False,
        server_default="routine",
    )
    channel: Mapped[str] = mapped_column(
        Enum(ConsultationChannel, name="consultation_channel"), nullable=False
    )
    farmer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    prescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    video_call_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    animal = relationship("Animal", lazy="noload")
    farmer = relationship("User", foreign_keys=[farmer_id], lazy="noload")
    vet = relationship("User", foreign_keys=[vet_id], lazy="noload")
