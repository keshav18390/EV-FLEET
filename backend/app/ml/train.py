"""
Trains and saves 4 scikit-learn models used by the platform:
  1. Battery Health Predictor  (regressor: predicts battery SoH % from usage)
  2. Maintenance Predictor     (classifier: predicts whether service is due soon)
  3. Delivery Delay Predictor  (classifier: predicts whether a delivery will be delayed)
  4. Rider Performance Scorer  (regressor: predicts rider performance score)

Trained on the seeded SQLite database, so run `python -m app.seed` first.
Models are saved to app/ml/models/*.joblib and auto-loaded by app/ml/predict.py.

Run with:  python -m app.ml.train
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score

from app.db.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.rider import Rider
from app.models.delivery import Delivery, DeliveryStatus

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def train_battery_health_model(db):
    rows = db.query(Vehicle).all()
    df = pd.DataFrame(
        [
            {
                "odometer_km": v.odometer_km,
                "total_charge_cycles": v.total_charge_cycles,
                "avg_daily_km": v.avg_daily_km,
                "battery_health": v.battery_health,
            }
            for v in rows
        ]
    )
    X = df[["odometer_km", "total_charge_cycles", "avg_daily_km"]]
    y = df["battery_health"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"[battery_health] MAE: {mae:.2f} percentage points")

    joblib.dump(model, f"{MODELS_DIR}/battery_health_model.joblib")


def train_maintenance_model(db):
    rows = db.query(Vehicle).all()
    df = pd.DataFrame(
        [
            {
                "odometer_km": v.odometer_km,
                "total_charge_cycles": v.total_charge_cycles,
                "battery_health": v.battery_health,
                "avg_daily_km": v.avg_daily_km,
                "needs_service": int(
                    v.next_service_due_km is not None and v.odometer_km >= v.next_service_due_km
                ),
            }
            for v in rows
        ]
    )
    X = df[["odometer_km", "total_charge_cycles", "battery_health", "avg_daily_km"]]
    y = df["needs_service"]

    if y.nunique() < 2:
        print("[maintenance] Not enough class variety in seed data, skipping training (using heuristic fallback).")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"[maintenance] Accuracy: {acc:.2%}")

    joblib.dump(model, f"{MODELS_DIR}/maintenance_model.joblib")


def train_delivery_delay_model(db):
    rows = db.query(Delivery).all()
    df = pd.DataFrame(
        [
            {
                "distance_km": d.distance_km,
                "hour_of_day": d.scheduled_time.hour,
                "day_of_week": d.scheduled_time.weekday(),
                "is_delayed": int(d.status == DeliveryStatus.delayed),
            }
            for d in rows
        ]
    )
    X = df[["distance_km", "hour_of_day", "day_of_week"]]
    y = df["is_delayed"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"[delivery_delay] Accuracy: {acc:.2%}")

    joblib.dump(model, f"{MODELS_DIR}/delivery_delay_model.joblib")


def train_rider_performance_model(db):
    rows = db.query(Rider).all()
    df = pd.DataFrame(
        [
            {
                "total_deliveries": r.total_deliveries,
                "on_time_rate": r.on_time_rate,
                "rating": r.rating,
                "performance_score": r.performance_score,
            }
            for r in rows
        ]
    )
    X = df[["total_deliveries", "on_time_rate", "rating"]]
    y = df["performance_score"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, model.predict(X_test))
    print(f"[rider_performance] MAE: {mae:.2f} points")

    joblib.dump(model, f"{MODELS_DIR}/rider_performance_model.joblib")


def main():
    import os
    os.makedirs(MODELS_DIR, exist_ok=True)
    db = SessionLocal()
    try:
        train_battery_health_model(db)
        train_maintenance_model(db)
        train_delivery_delay_model(db)
        train_rider_performance_model(db)
        print("\nAll models trained and saved to app/ml/models/")
    finally:
        db.close()


if __name__ == "__main__":
    main()
