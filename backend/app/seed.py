"""
Seeds the database with realistic demo data:
  - 50 vehicles, 50 riders, 500 deliveries, 100+ maintenance records
  - 3 demo login users (admin / fleet manager / operations manager)
  - A handful of alerts derived from the generated data

Run with:  python -m app.seed
"""
import random
from datetime import datetime, timedelta, timezone

from faker import Faker

from app.db.database import Base, engine, SessionLocal
from app import models  # noqa: F401
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.rider import Rider, RiderStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.models.maintenance import MaintenanceRecord, MaintenanceType
from app.models.alert import Alert, AlertType, AlertSeverity
from app.core.security import hash_password

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

CITIES = ["Jaipur", "Delhi", "Bangalore", "Mumbai", "Hyderabad", "Pune"]
VEHICLE_MODELS = ["Zypp Zomo E1", "Zypp Zomo E2", "Bounce Infinity", "Ather Rizta", "Ola S1 Cargo"]
AREAS = [
    "Malviya Nagar", "C-Scheme", "Vaishali Nagar", "Mansarovar", "Jagatpura",
    "Tonk Road", "Sanganer", "Vidhyadhar Nagar", "Raja Park", "Civil Lines",
]


def random_date(days_back: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))


def seed_users(db):
    demo_users = [
        ("Admin User", "admin@evfleet.com", "Admin@123", UserRole.admin),
        ("Fleet Manager", "fleetmanager@evfleet.com", "Fleet@123", UserRole.fleet_manager),
        ("Ops Manager", "opsmanager@evfleet.com", "Ops@123", UserRole.operations_manager),
    ]
    for name, email, pwd, role in demo_users:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(full_name=name, email=email, hashed_password=hash_password(pwd), role=role))
    db.commit()
    print("Seeded demo users (admin@evfleet.com / Admin@123, etc.)")


def seed_vehicles(db, count=50):
    vehicles = []
    for i in range(count):
        battery_health = round(random.uniform(55, 100), 1)
        odometer = round(random.uniform(500, 25000), 1)
        status = random.choices(
            [VehicleStatus.active, VehicleStatus.charging, VehicleStatus.maintenance, VehicleStatus.idle],
            weights=[60, 15, 10, 15],
        )[0]
        v = Vehicle(
            registration_number=f"RJ14{random.choice('ABCDEFGH')}{random.randint(1000,9999)}",
            model=random.choice(VEHICLE_MODELS),
            city=random.choice(CITIES),
            status=status,
            battery_level=round(random.uniform(5, 100), 1),
            battery_health=battery_health,
            odometer_km=odometer,
            total_charge_cycles=random.randint(50, 900),
            avg_daily_km=round(random.uniform(30, 120), 1),
            latitude=26.9124 + random.uniform(-0.15, 0.15),
            longitude=75.7873 + random.uniform(-0.15, 0.15),
            last_service_date=random_date(120),
            next_service_due_km=round(odometer + random.uniform(-500, 1500), 1),
            purchase_date=random_date(700),
            fleet_health_score=round((battery_health * 0.6) + random.uniform(0, 40), 1),
        )
        v.fleet_health_score = min(100, round(v.fleet_health_score, 1))
        vehicles.append(v)
    db.add_all(vehicles)
    db.commit()
    print(f"Seeded {count} vehicles")
    return vehicles


def seed_riders(db, count=50):
    riders = []
    for i in range(count):
        score = round(random.uniform(40, 100), 1)
        r = Rider(
            full_name=fake.name(),
            phone=f"9{random.randint(100000000, 999999999)}",
            city=random.choice(CITIES),
            status=random.choices(
                [RiderStatus.active, RiderStatus.on_trip, RiderStatus.offline],
                weights=[50, 25, 25],
            )[0],
            rating=round(random.uniform(3.2, 5.0), 1),
            total_deliveries=random.randint(20, 1200),
            on_time_rate=round(random.uniform(60, 99.5), 1),
            performance_score=score,
            joined_date=random_date(500),
        )
        riders.append(r)
    db.add_all(riders)
    db.commit()
    print(f"Seeded {count} riders")
    return riders


def seed_deliveries(db, vehicles, riders, count=500):
    deliveries = []
    for i in range(count):
        status = random.choices(
            [DeliveryStatus.completed, DeliveryStatus.delayed, DeliveryStatus.cancelled, DeliveryStatus.in_progress],
            weights=[70, 15, 5, 10],
        )[0]
        scheduled = random_date(30)
        delay = round(random.uniform(5, 90), 1) if status == DeliveryStatus.delayed else 0.0
        completed_time = scheduled + timedelta(minutes=delay + random.uniform(10, 40)) if status in (
            DeliveryStatus.completed, DeliveryStatus.delayed
        ) else None

        d = Delivery(
            vehicle_id=random.choice(vehicles).id,
            rider_id=random.choice(riders).id,
            pickup_area=random.choice(AREAS),
            drop_area=random.choice(AREAS),
            distance_km=round(random.uniform(1.5, 18), 2),
            status=status,
            scheduled_time=scheduled,
            completed_time=completed_time,
            delay_minutes=delay,
        )
        deliveries.append(d)
    db.add_all(deliveries)
    db.commit()
    print(f"Seeded {count} deliveries")


def seed_maintenance(db, vehicles, count=110):
    records = []
    for i in range(count):
        vehicle = random.choice(vehicles)
        m_type = random.choice(list(MaintenanceType))
        cost_map = {
            MaintenanceType.battery_replacement: (8000, 25000),
            MaintenanceType.tire_change: (800, 2500),
            MaintenanceType.brake_service: (500, 1800),
            MaintenanceType.general_checkup: (300, 900),
            MaintenanceType.motor_repair: (2000, 9000),
        }
        low, high = cost_map[m_type]
        records.append(
            MaintenanceRecord(
                vehicle_id=vehicle.id,
                maintenance_type=m_type,
                description=f"{m_type.value.replace('_', ' ').title()} performed",
                cost=round(random.uniform(low, high), 2),
                performed_at=random_date(180),
                odometer_at_service=round(vehicle.odometer_km - random.uniform(0, 2000), 1),
            )
        )
    db.add_all(records)
    db.commit()
    print(f"Seeded {count} maintenance records")


def seed_alerts(db, vehicles, riders):
    alerts = []
    for v in vehicles:
        if v.battery_level < 20:
            alerts.append(
                Alert(
                    vehicle_id=v.id,
                    alert_type=AlertType.low_battery,
                    severity=AlertSeverity.high if v.battery_level < 10 else AlertSeverity.medium,
                    message=f"Vehicle {v.registration_number} battery at {v.battery_level}%",
                )
            )
        if v.battery_health < 70:
            alerts.append(
                Alert(
                    vehicle_id=v.id,
                    alert_type=AlertType.battery_degradation,
                    severity=AlertSeverity.critical if v.battery_health < 60 else AlertSeverity.medium,
                    message=f"Vehicle {v.registration_number} battery health degraded to {v.battery_health}%",
                )
            )
        if v.next_service_due_km and v.odometer_km >= v.next_service_due_km:
            alerts.append(
                Alert(
                    vehicle_id=v.id,
                    alert_type=AlertType.maintenance_due,
                    severity=AlertSeverity.medium,
                    message=f"Vehicle {v.registration_number} is due for maintenance",
                )
            )
    for r in riders:
        if r.performance_score < 50:
            alerts.append(
                Alert(
                    rider_id=r.id,
                    alert_type=AlertType.rider_performance,
                    severity=AlertSeverity.low,
                    message=f"Rider {r.full_name} performance score below threshold ({r.performance_score})",
                )
            )
    db.add_all(alerts)
    db.commit()
    print(f"Seeded {len(alerts)} alerts")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Vehicle).count() > 0:
            print("Database already contains data. Skipping seed. Delete fleet.db to reseed.")
            return
        seed_users(db)
        vehicles = seed_vehicles(db, 50)
        riders = seed_riders(db, 50)
        seed_deliveries(db, vehicles, riders, 500)
        seed_maintenance(db, vehicles, 110)
        seed_alerts(db, vehicles, riders)
        print("\nSeed complete. Demo logins:")
        print("  admin@evfleet.com / Admin@123")
        print("  fleetmanager@evfleet.com / Fleet@123")
        print("  opsmanager@evfleet.com / Ops@123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
