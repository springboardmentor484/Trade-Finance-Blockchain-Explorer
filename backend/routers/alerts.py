from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Alert
from backend.utils import get_current_user
from backend.models import User

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# 🔹 Get all alerts
@router.get("/")
def list_alerts(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    alerts = session.exec(select(Alert)).all()
    return alerts


# 🔹 Get single alert
@router.get("/{alert_id}")
def get_alert(
    alert_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    alert = session.get(Alert, alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert