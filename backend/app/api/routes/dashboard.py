from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.fleet import DashboardKPIs
from app.core.deps import get_current_user
from app.agents.tools import get_fleet_summary

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def dashboard_kpis(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    summary = get_fleet_summary(db)
    return DashboardKPIs(**summary)
