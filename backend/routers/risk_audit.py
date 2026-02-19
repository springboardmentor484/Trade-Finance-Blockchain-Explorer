from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(
    prefix="/risk-audit",
    tags=["Risk & Audit"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a RiskScore
@router.post("/risk-scores")
def create_risk_score(user_id: int, score: float, rationale: str, db: Session = Depends(get_db)):
    risk = models.RiskScore(user_id=user_id, score=score, rationale=rationale)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk

# Get all RiskScores
@router.get("/risk-scores")
def list_risk_scores(db: Session = Depends(get_db)):
    return db.query(models.RiskScore).all()

# Create an AuditLog
@router.post("/audit-logs")
def create_audit_log(admin_id: int, action: str, target_type: str, target_id: int = None, db: Session = Depends(get_db)):
    log = models.AuditLog(admin_id=admin_id, action=action, target_type=target_type, target_id=target_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# Get all AuditLogs
@router.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(models.AuditLog).all()