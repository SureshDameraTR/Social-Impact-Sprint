import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class AlertSeverity(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    severe = "severe"
    extreme = "extreme"


class WeatherAlert(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "weather_alerts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(
        Enum(AlertSeverity, name="alert_severity"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="IMD", server_default="IMD")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
