from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.rider import Rider, RiderStatus
from app.schemas.fleet import RiderOut, PaginatedResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/riders", tags=["Riders"])


@router.get("", response_model=PaginatedResponse)
def list_riders(
    search: Optional[str] = None,
    status_filter: Optional[RiderStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Rider)
    if search:
        q = q.filter(or_(Rider.full_name.ilike(f"%{search}%"), Rider.phone.ilike(f"%{search}%")))
    if status_filter:
        q = q.filter(Rider.status == status_filter)

    total = q.count()
    items = q.order_by(Rider.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=[RiderOut.model_validate(r) for r in items]
    )


@router.get("/{rider_id}", response_model=RiderOut)
def get_rider(rider_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider
