import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    fleet_manager = "fleet_manager"
    operations_manager = "operations_manager"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.operations_manager, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
