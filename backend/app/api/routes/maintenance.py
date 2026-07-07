from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.maintenance import MaintenanceRecord
from app.schemas.fleet import MaintenanceOut, PaginatedResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("", response_model=PaginatedResponse)
def list_maintenance(
    vehicle_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(MaintenanceRecord)
    if vehicle_id:
        q = q.filter(MaintenanceRecord.vehicle_id == vehicle_id)

    total = q.count()
    items = (
        q.order_by(MaintenanceRecord.performed_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )
    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=[MaintenanceOut.model_validate(m) for m in items]
    )
