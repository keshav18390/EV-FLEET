import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from app.db.database import Base


class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertType(str, enum.Enum):
    low_battery = "low_battery"
    maintenance_due = "maintenance_due"
    delivery_delay = "delivery_delay"
    battery_degradation = "battery_degradation"
    rider_performance = "rider_performance"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    rider_id = Column(Integer, ForeignKey("riders.id"), nullable=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.medium, nullable=False)
    message = Column(String(255), nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
