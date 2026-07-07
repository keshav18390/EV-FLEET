from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.delivery import Delivery, DeliveryStatus
from app.schemas.fleet import DeliveryOut, PaginatedResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/deliveries", tags=["Deliveries"])


@router.get("", response_model=PaginatedResponse)
def list_deliveries(
    status_filter: Optional[DeliveryStatus] = Query(None, alias="status"),
    vehicle_id: Optional[int] = None,
    rider_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Delivery)
    if status_filter:
        q = q.filter(Delivery.status == status_filter)
    if vehicle_id:
        q = q.filter(Delivery.vehicle_id == vehicle_id)
    if rider_id:
        q = q.filter(Delivery.rider_id == rider_id)

    total = q.count()
    items = (
        q.order_by(Delivery.scheduled_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )
    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=[DeliveryOut.model_validate(d) for d in items]
    )
