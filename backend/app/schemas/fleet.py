from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.vehicle import VehicleStatus
from app.models.rider import RiderStatus
from app.models.delivery import DeliveryStatus
from app.models.maintenance import MaintenanceType
from app.models.alert import AlertSeverity, AlertType


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registration_number: str
    model: str
    city: str
    status: VehicleStatus
    battery_level: float
    battery_health: float
    odometer_km: float
    total_charge_cycles: int
    avg_daily_km: float
    latitude: float
    longitude: float
    last_service_date: Optional[datetime] = None
    next_service_due_km: Optional[float] = None
    fleet_health_score: float


class RiderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    phone: str
    city: str
    status: RiderStatus
    rating: float
    total_deliveries: int
    on_time_rate: float
    performance_score: float


class DeliveryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    rider_id: int
    pickup_area: str
    drop_area: str
    distance_km: float
    status: DeliveryStatus
    scheduled_time: datetime
    completed_time: Optional[datetime] = None
    delay_minutes: float


class MaintenanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: int
    maintenance_type: MaintenanceType
    description: Optional[str] = None
    cost: float
    performed_at: datetime
    odometer_at_service: float


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vehicle_id: Optional[int] = None
    rider_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    is_resolved: bool
    created_at: datetime


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


class DashboardKPIs(BaseModel):
    total_vehicles: int
    active_vehicles: int
    vehicles_in_maintenance: int
    avg_battery_level: float
    avg_fleet_health_score: float
    total_riders: int
    active_riders: int
    deliveries_today: int
    deliveries_delayed_today: int
    on_time_rate: float
    open_alerts: int
    critical_alerts: int


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    agent: str
