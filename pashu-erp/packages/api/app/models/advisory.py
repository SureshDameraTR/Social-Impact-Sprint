import enum
from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, DateTime, Enum, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class AdvisoryCategory(str, enum.Enum):
    health = "health"
    feeding = "feeding"
    breeding = "breeding"
    government = "government"


class AdvisorySource(str, enum.Enum):
    ICAR = "ICAR"
    KMF = "KMF"
    NABARD = "NABARD"
    Community = "Community"


class AdvisoryTip(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "advisory_tips"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title_en: Mapped[str] = mapped_column(String(300), nullable=False)
    title_kn: Mapped[str | None] = mapped_column(String(300), nullable=True)
    body_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_kn: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        Enum(AdvisoryCategory, name="advisory_category"), nullable=False
    )
    species_applicable: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(
        Enum(AdvisorySource, name="advisory_source"), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
