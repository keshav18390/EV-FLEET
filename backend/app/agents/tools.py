"""
Data-access helpers shared by every agent. Keeping DB logic here (instead of
inside each agent) means agents stay pure/testable and grounded in real data
instead of hallucinating numbers.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.rider import Rider, RiderStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.models.maintenance import MaintenanceRecord
from app.models.alert import Alert, AlertSeverity


def get_low_battery_vehicles(db: Session, threshold: float = 20.0, limit: int = 20):
    return (
        db.query(Vehicle)
        .filter(Vehicle.battery_level < threshold)
        .order_by(Vehicle.battery_level.asc())
        .limit(limit)
        .all()
    )


def get_vehicles_needing_service(db: Session, limit: int = 20):
    return (
        db.query(Vehicle)
        .filter(
            (Vehicle.next_service_due_km.isnot(None))
            & (Vehicle.odometer_km >= Vehicle.next_service_due_km)
        )
        .order_by(Vehicle.fleet_health_score.asc())
        .limit(limit)
        .all()
    )

def get_degrading_battery_vehicles(db: Session, health_threshold: float = 75.0, limit: int = 20):
    return (
        db.query(Vehicle)
        .filter(Vehicle.battery_health < health_threshold)
        .order_by(Vehicle.battery_health.asc())
        .limit(limit)
        .all()
    )


def get_worst_riders(db: Session, limit: int = 10):
    return (
        db.query(Rider)
        .order_by(Rider.performance_score.asc())
        .limit(limit)
        .all()
    )


def get_best_riders(db: Session, limit: int = 10):
    return (
        db.query(Rider)
        .order_by(Rider.performance_score.desc())
        .limit(limit)
        .all()
    )


def get_fleet_summary(db: Session) -> dict:
    total_vehicles = db.query(Vehicle).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.active).count()
    maintenance_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.maintenance).count()
    avg_battery = db.query(func.avg(Vehicle.battery_level)).scalar() or 0.0
    avg_health_score = db.query(func.avg(Vehicle.fleet_health_score)).scalar() or 0.0
    avg_battery_health = db.query(func.avg(Vehicle.battery_health)).scalar() or 0.0

    total_riders = db.query(Rider).count()
    active_riders = db.query(Rider).filter(Rider.status == RiderStatus.active).count()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    deliveries_today = db.query(Delivery).filter(Delivery.scheduled_time >= today_start).count()
    delayed_today = (
        db.query(Delivery)
        .filter(Delivery.scheduled_time >= today_start, Delivery.status == DeliveryStatus.delayed)
        .count()
    )
    completed = db.query(Delivery).filter(Delivery.status == DeliveryStatus.completed).count()
    total_deliveries = db.query(Delivery).count()
    on_time_rate = (completed / total_deliveries * 100) if total_deliveries else 100.0

    open_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()  # noqa: E712
    critical_alerts = (
        db.query(Alert)
        .filter(Alert.is_resolved == False, Alert.severity == AlertSeverity.critical)  # noqa: E712
        .count()
    )

    return {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "vehicles_in_maintenance": maintenance_vehicles,
        "avg_battery_level": round(avg_battery, 1),
        "avg_battery_health": round(avg_battery_health, 1),
        "avg_fleet_health_score": round(avg_health_score, 1),
        "total_riders": total_riders,
        "active_riders": active_riders,
        "deliveries_today": deliveries_today,
        "deliveries_delayed_today": delayed_today,
        "on_time_rate": round(on_time_rate, 1),
        "open_alerts": open_alerts,
        "critical_alerts": critical_alerts,
    }


def get_recent_delayed_deliveries(db: Session, days: int = 7, limit: int = 20):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return (
        db.query(Delivery)
        .filter(Delivery.status == DeliveryStatus.delayed, Delivery.scheduled_time >= since)
        .order_by(Delivery.delay_minutes.desc())
        .limit(limit)
        .all()
    )


def get_maintenance_cost_summary(db: Session) -> dict:
    total_cost = db.query(func.sum(MaintenanceRecord.cost)).scalar() or 0.0
    record_count = db.query(MaintenanceRecord).count()
    return {"total_cost": round(total_cost, 2), "record_count": record_count}
