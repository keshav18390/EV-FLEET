import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class RiderStatus(str, enum.Enum):
    active = "active"
    on_trip = "on_trip"
    offline = "offline"
    suspended = "suspended"


class Rider(Base):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    city = Column(String(60), nullable=False)
    status = Column(Enum(RiderStatus), default=RiderStatus.active, nullable=False)

    rating = Column(Float, default=5.0)
    total_deliveries = Column(Integer, default=0)
    on_time_rate = Column(Float, default=100.0)
    performance_score = Column(Float, default=80.0)

    joined_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    deliveries = relationship("Delivery", back_populates="rider")
