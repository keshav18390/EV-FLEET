from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alert import Alert, AlertSeverity
from app.schemas.fleet import AlertOut, PaginatedResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse)
def list_alerts(
    severity: Optional[AlertSeverity] = None,
    resolved: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity)
    if resolved is not None:
        q = q.filter(Alert.is_resolved == resolved)

    total = q.count()
    items = q.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=[AlertOut.model_validate(a) for a in items]
    )


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = True
    db.commit()
    db.refresh(alert)
    return alert
