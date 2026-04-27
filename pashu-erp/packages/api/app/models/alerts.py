import enum
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class CommunityAlertSeverity(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


class CommunityAlert(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "community_alerts"
    __table_args__ = (
        CheckConstraint("lat BETWEEN -90 AND 90", name="ck_community_alerts_lat_range"),
        CheckConstraint("lon BETWEEN -180 AND 180", name="ck_community_alerts_lon_range"),
        CheckConstraint("radius_km > 0", name="ck_community_alerts_radius_positive"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    reported_by: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    disease_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    radius_km: Mapped[float] = mapped_column(Numeric(7, 2), default=5.0, server_default="5.0")
    severity: Mapped[str] = mapped_column(
        Enum(CommunityAlertSeverity, name="community_alert_severity"), nullable=False
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by], lazy="noload")
