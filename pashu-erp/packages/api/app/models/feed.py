import enum
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Enum, Numeric, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class FeedCategory(str, enum.Enum):
    roughage = "roughage"
    concentrate = "concentrate"
    supplement = "supplement"
    mineral = "mineral"


class FeedIngredient(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "feed_ingredients"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_kn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(
        Enum(FeedCategory, name="feed_category"), nullable=False
    )
    protein_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    energy_kcal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cost_per_kg: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    availability_season: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_available: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
