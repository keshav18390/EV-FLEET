from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.vehicle import Vehicle
from app.models.rider import Rider
from app.core.deps import get_current_user
from app.ml.predict import (
    predict_battery_health,
    predict_maintenance_needed,
    predict_delivery_delay,
    predict_rider_performance,
)

router = APIRouter(prefix="/api/ml", tags=["ML Predictions"])


@router.get("/vehicle/{vehicle_id}/battery-health-forecast")
def battery_health_forecast(vehicle_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    predicted = predict_battery_health(v.odometer_km, v.total_charge_cycles, v.avg_daily_km)
    return {"vehicle_id": vehicle_id, "current_battery_health": v.battery_health, "predicted_battery_health": predicted}


@router.get("/vehicle/{vehicle_id}/maintenance-prediction")
def maintenance_prediction(vehicle_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    needed = predict_maintenance_needed(v.odometer_km, v.total_charge_cycles, v.battery_health, v.avg_daily_km)
    return {"vehicle_id": vehicle_id, "maintenance_recommended": needed}


@router.get("/delivery-delay-risk")
def delivery_delay_risk(
    distance_km: float,
    hour_of_day: int = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    hour = hour_of_day if hour_of_day is not None else datetime.now(timezone.utc).hour
    day_of_week = datetime.now(timezone.utc).weekday()
    at_risk = predict_delivery_delay(distance_km, hour, day_of_week)
    return {"distance_km": distance_km, "hour_of_day": hour, "delay_risk": at_risk}


@router.get("/rider/{rider_id}/performance-forecast")
def rider_performance_forecast(rider_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    r = db.query(Rider).filter(Rider.id == rider_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rider not found")
    predicted = predict_rider_performance(r.total_deliveries, r.on_time_rate, r.rating)
    return {"rider_id": rider_id, "current_score": r.performance_score, "predicted_score": predicted}
