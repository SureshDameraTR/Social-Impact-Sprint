import enum
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EvidenceRating(str, enum.Enum):
    traditional = "traditional"
    studied = "studied"
    icar_validated = "icar_validated"


class TraditionalRemedy(Base):
    __tablename__ = "traditional_remedies"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_kn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    plant_ingredient: Mapped[str] = mapped_column(String(200), nullable=False)
    preparation_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    dosage_by_species: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    conditions_treated: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evidence_rating: Mapped[str] = mapped_column(
        Enum(EvidenceRating, name="evidence_rating"), nullable=False
    )
    safety_warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
