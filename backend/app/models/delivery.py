import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class DeliveryStatus(str, enum.Enum):
    completed = "completed"
    delayed = "delayed"
    cancelled = "cancelled"
    in_progress = "in_progress"


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    rider_id = Column(Integer, ForeignKey("riders.id"), nullable=False)

    pickup_area = Column(String(100), nullable=False)
    drop_area = Column(String(100), nullable=False)
    distance_km = Column(Float, default=0.0)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.completed, nullable=False)

    scheduled_time = Column(DateTime, nullable=False)
    completed_time = Column(DateTime, nullable=True)
    delay_minutes = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vehicle = relationship("Vehicle", back_populates="deliveries")
    rider = relationship("Rider", back_populates="deliveries")
