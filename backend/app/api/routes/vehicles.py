from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.fleet import VehicleOut, PaginatedResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


@router.get("", response_model=PaginatedResponse)
def list_vehicles(
    search: Optional[str] = None,
    status_filter: Optional[VehicleStatus] = Query(None, alias="status"),
    city: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Vehicle)
    if search:
        q = q.filter(or_(Vehicle.registration_number.ilike(f"%{search}%"), Vehicle.model.ilike(f"%{search}%")))
    if status_filter:
        q = q.filter(Vehicle.status == status_filter)
    if city:
        q = q.filter(Vehicle.city == city)

    total = q.count()
    items = q.order_by(Vehicle.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=[VehicleOut.model_validate(v) for v in items]
    )


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("/low-battery/list", response_model=list[VehicleOut])
def low_battery_vehicles(threshold: float = 20.0, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    vehicles = db.query(Vehicle).filter(Vehicle.battery_level < threshold).order_by(Vehicle.battery_level).all()
    return vehicles
