"""
Loads trained models (if present) and exposes simple predict_* functions.
If a model file is missing (e.g. `train.py` hasn't been run yet), falls back
to a reasonable heuristic instead of crashing -- keeps the API always usable.
"""
import os
import joblib
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

_cache = {}


def _load(name: str):
    if name in _cache:
        return _cache[name]
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    if os.path.exists(path):
        _cache[name] = joblib.load(path)
    else:
        _cache[name] = None
    return _cache[name]


def predict_battery_health(odometer_km: float, total_charge_cycles: int, avg_daily_km: float) -> float:
    model = _load("battery_health_model")
    if model is None:
        # Heuristic fallback: degrade ~0.002%/km and ~0.01%/cycle from 100%
        return round(max(40.0, 100 - odometer_km * 0.002 - total_charge_cycles * 0.01), 1)
    pred = model.predict(np.array([[odometer_km, total_charge_cycles, avg_daily_km]]))[0]
    return round(float(pred), 1)


def predict_maintenance_needed(odometer_km: float, total_charge_cycles: int, battery_health: float, avg_daily_km: float) -> bool:
    model = _load("maintenance_model")
    if model is None:
        return battery_health < 65 or odometer_km > 20000
    pred = model.predict(np.array([[odometer_km, total_charge_cycles, battery_health, avg_daily_km]]))[0]
    return bool(pred)


def predict_delivery_delay(distance_km: float, hour_of_day: int, day_of_week: int) -> bool:
    model = _load("delivery_delay_model")
    if model is None:
        return distance_km > 12 or hour_of_day in (8, 9, 18, 19)
    pred = model.predict(np.array([[distance_km, hour_of_day, day_of_week]]))[0]
    return bool(pred)


def predict_rider_performance(total_deliveries: int, on_time_rate: float, rating: float) -> float:
    model = _load("rider_performance_model")
    if model is None:
        return round(min(100.0, on_time_rate * 0.6 + rating * 8), 1)
    pred = model.predict(np.array([[total_deliveries, on_time_rate, rating]]))[0]
    return round(float(pred), 1)
