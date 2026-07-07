import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class MaintenanceType(str, enum.Enum):
    battery_replacement = "battery_replacement"
    tire_change = "tire_change"
    brake_service = "brake_service"
    general_checkup = "general_checkup"
    motor_repair = "motor_repair"


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(String(255), nullable=True)
    cost = Column(Float, default=0.0)
    performed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    odometer_at_service = Column(Float, default=0.0)

    vehicle = relationship("Vehicle", back_populates="maintenance_records")
