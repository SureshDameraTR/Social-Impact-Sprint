import enum
from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, Enum, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class AlertSeverity(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


class CommunityAlert(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "community_alerts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    reported_by: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, default=5.0, server_default="5.0")
    severity: Mapped[str] = mapped_column(
        Enum(AlertSeverity, name="community_alert_severity"), nullable=False
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by], lazy="noload")
