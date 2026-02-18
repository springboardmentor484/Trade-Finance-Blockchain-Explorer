from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import get_session
from app.models import (
    User, RiskScore, TradeTransaction, TransactionStatusEnum
)

router = APIRouter(prefix="/risk", tags=["risk"])


class RiskScoreResponse(BaseModel):
    """Risk score response"""
    user_id: int
    user_name: str
    email: str
    completed_count: int
    total_count: int
    disputed_count: int
    risk_score: float
    rationale: str
    last_updated: str


class RiskSummaryResponse(BaseModel):
    """Risk summary response"""
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_risk_score: float
    top_risky_users: List[RiskScoreResponse]


def calculate_risk_score(user_id: int, session: Session) -> dict:
    """Calculate risk score for a user"""
    
    # Get all transactions for user as buyer or seller
    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id) |
            (TradeTransaction.seller_id == user_id)
        )
    ).all()
    
    if not transactions:
        return {
            "completed_count": 0,
            "total_count": 0,
            "disputed_count": 0,
            "risk_score": 0.0,
            "rationale": "No transactions yet"
        }
    
    total_count = len(transactions)
    completed_count = sum(
        1 for t in transactions 
        if t.status == TransactionStatusEnum.COMPLETED
    )
    disputed_count = sum(
        1 for t in transactions 
        if t.status == TransactionStatusEnum.DISPUTED
    )
    
    # Calculate risk score
    if total_count == 0:
        risk_score = 0.0
    else:
        risk_score = (disputed_count / total_count) * 100
    
    # Determine rationale
    if risk_score == 0:
        rationale = "No disputes recorded"
    elif risk_score < 10:
        rationale = "Low risk - minimal disputes"
    elif risk_score < 30:
        rationale = "Medium risk - some disputes"
    else:
        rationale = "High risk - frequent disputes"
    
    return {
        "completed_count": completed_count,
        "total_count": total_count,
        "disputed_count": disputed_count,
        "risk_score": round(risk_score, 2),
        "rationale": rationale
    }


@router.get("/score/{user_id}", response_model=RiskScoreResponse, summary="Get risk score for user")
def get_risk_score(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get risk score for a specific user"""
    
    # Fetch user
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate risk score
    score_data = calculate_risk_score(user_id, session)
    
    # Update or create risk score in database
    risk_score = session.exec(
        select(RiskScore).where(RiskScore.user_id == user_id)
    ).first()
    
    if risk_score:
        risk_score.completed_count = score_data["completed_count"]
        risk_score.total_count = score_data["total_count"]
        risk_score.disputed_count = score_data["disputed_count"]
        risk_score.risk_score = score_data["risk_score"]
        risk_score.rationale = score_data["rationale"]
        risk_score.last_updated = datetime.utcnow()
    else:
        risk_score = RiskScore(
            user_id=user_id,
            completed_count=score_data["completed_count"],
            total_count=score_data["total_count"],
            disputed_count=score_data["disputed_count"],
            risk_score=score_data["risk_score"],
            rationale=score_data["rationale"]
        )
    
    session.add(risk_score)
    session.commit()
    session.refresh(risk_score)
    
    return RiskScoreResponse(
        user_id=risk_score.user_id,
        user_name=user.name,
        email=user.email,
        completed_count=risk_score.completed_count,
        total_count=risk_score.total_count,
        disputed_count=risk_score.disputed_count,
        risk_score=risk_score.risk_score,
        rationale=risk_score.rationale,
        last_updated=risk_score.last_updated.isoformat()
    )


@router.get("/summary", response_model=RiskSummaryResponse, summary="Get risk summary")
def get_risk_summary(session: Session = Depends(get_session)):
    """Get overall risk summary"""
    
    # Get all risk scores
    risk_scores = session.exec(select(RiskScore)).all()
    
    if not risk_scores:
        return RiskSummaryResponse(
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            average_risk_score=0.0,
            top_risky_users=[]
        )
    
    # Count by risk level
    high_risk = sum(1 for rs in risk_scores if rs.risk_score >= 30)
    medium_risk = sum(1 for rs in risk_scores if 10 <= rs.risk_score < 30)
    low_risk = sum(1 for rs in risk_scores if rs.risk_score < 10)
    
    # Average risk score
    avg_risk = sum(rs.risk_score for rs in risk_scores) / len(risk_scores)
    
    # Top 3 risky users
    top_risky = sorted(risk_scores, key=lambda x: x.risk_score, reverse=True)[:3]
    
    top_risky_users = []
    for rs in top_risky:
        user = session.exec(select(User).where(User.id == rs.user_id)).first()
        if user:
            top_risky_users.append(
                RiskScoreResponse(
                    user_id=rs.user_id,
                    user_name=user.name,
                    email=user.email,
                    completed_count=rs.completed_count,
                    total_count=rs.total_count,
                    disputed_count=rs.disputed_count,
                    risk_score=rs.risk_score,
                    rationale=rs.rationale,
                    last_updated=rs.last_updated.isoformat()
                )
            )
    
    return RiskSummaryResponse(
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        average_risk_score=round(avg_risk, 2),
        top_risky_users=top_risky_users
    )


@router.get("/all", summary="Get all risk scores")
def get_all_risk_scores(
    session: Session = Depends(get_session),
    limit: int = 100,
    offset: int = 0
):
    """Get all risk scores with pagination"""
    
    risk_scores = session.exec(
        select(RiskScore)
        .order_by(RiskScore.risk_score.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    total = session.exec(select(func.count(RiskScore.id))).one()
    
    risk_data = []
    for rs in risk_scores:
        user = session.exec(select(User).where(User.id == rs.user_id)).first()
        if user:
            risk_data.append({
                "user_id": rs.user_id,
                "user_name": user.name,
                "email": user.email,
                "completed_count": rs.completed_count,
                "total_count": rs.total_count,
                "disputed_count": rs.disputed_count,
                "risk_score": rs.risk_score,
                "rationale": rs.rationale
            })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": risk_data
    }
