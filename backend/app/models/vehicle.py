import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class VehicleStatus(str, enum.Enum):
    active = "active"
    charging = "charging"
    maintenance = "maintenance"
    idle = "idle"
    out_of_service = "out_of_service"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(30), unique=True, index=True, nullable=False)
    model = Column(String(60), nullable=False)
    city = Column(String(60), nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.active, nullable=False)

    battery_level = Column(Float, default=100.0)          # % current charge
    battery_health = Column(Float, default=100.0)         # % state of health
    odometer_km = Column(Float, default=0.0)
    total_charge_cycles = Column(Integer, default=0)
    avg_daily_km = Column(Float, default=0.0)

    latitude = Column(Float, default=26.9124)
    longitude = Column(Float, default=75.7873)

    last_service_date = Column(DateTime, nullable=True)
    next_service_due_km = Column(Float, nullable=True)
    purchase_date = Column(DateTime, nullable=True)

    fleet_health_score = Column(Float, default=100.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    deliveries = relationship("Delivery", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")
