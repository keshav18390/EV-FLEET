import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.db.database import get_db
from app.models.vehicle import Vehicle
from app.core.deps import get_current_user
from app.agents.tools import get_fleet_summary

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/vehicles/csv")
def export_vehicles_csv(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    vehicles = db.query(Vehicle).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["ID", "Registration", "Model", "City", "Status", "Battery %", "Battery Health %", "Odometer km", "Fleet Health Score"]
    )
    for v in vehicles:
        writer.writerow(
            [v.id, v.registration_number, v.model, v.city, v.status.value, v.battery_level, v.battery_health, v.odometer_km, v.fleet_health_score]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vehicles_report.csv"},
    )


@router.get("/fleet-summary/pdf")
def export_fleet_summary_pdf(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    summary = get_fleet_summary(db)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "EV Fleet Intelligence -- Fleet Summary Report")

    c.setFont("Helvetica", 11)
    y = height - 110
    for label, value in summary.items():
        c.drawString(50, y, f"{label.replace('_', ' ').title()}: {value}")
        y -= 22

    c.showPage()
    c.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=fleet_summary_report.pdf"},
    )
