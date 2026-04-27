import enum

from sqlalchemy import Boolean, CheckConstraint, Enum, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class FeedCategory(str, enum.Enum):
    roughage = "roughage"
    concentrate = "concentrate"
    supplement = "supplement"
    mineral = "mineral"


class FeedIngredient(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "feed_ingredients"
    __table_args__ = (
        CheckConstraint(
            "protein_pct BETWEEN 0 AND 100", name="ck_feed_ingredients_protein_pct_range"
        ),
        CheckConstraint("energy_kcal >= 0", name="ck_feed_ingredients_energy_non_negative"),
        CheckConstraint("cost_per_kg > 0", name="ck_feed_ingredients_cost_positive"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_kn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(Enum(FeedCategory, name="feed_category"), nullable=False)
    protein_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    energy_kcal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    cost_per_kg: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    availability_season: Mapped[str | None] = mapped_column(String(100), nullable=True)
    locally_available: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
