"""
Risk Scoring Engine for Trade Finance
Calculates counterparty and transaction risk
"""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from ..models import User, TradeTransaction, UserRole


def calculate_user_risk_score(user: User) -> tuple[float, dict]:
    """
    Calculate user's risk score based on transaction history
    Formula: risk = disputed / (completed + disputed) * 100
    
    Returns: (risk_score: 0-100, risk_factors: dict)
    """
    risk_factors = {}
    
    total_transactions = user.completed_transactions + user.disputed_transactions
    
    if total_transactions == 0:
        # New user with no transaction history
        return 50.0, {"status": "new_user"}
    
    # Calculate risk percentage
    risk_score = (user.disputed_transactions / total_transactions) * 100
    success_rate = (user.completed_transactions / total_transactions) * 100
    
    risk_factors = {
        "completed": user.completed_transactions,
        "disputed": user.disputed_transactions,
        "total": total_transactions,
        "success_rate": round(success_rate, 1),
        "risk_percentage": round(risk_score, 1),
    }
    
    return round(risk_score, 2), risk_factors


def calculate_risk_score(
    buyer: User,
    seller: User,
    amount: float,
    session: Session
) -> tuple[float, dict]:
    """
    Calculate risk score (0-100) and risk factors for a transaction
    Higher score = higher risk
    
    Risk factors considered:
    - User risk scores (based on transaction history)
    - New user (within 30 days)
    - High transaction amount vs user history
    - Counterparty payment history
    - Role mismatches
    """
    
    risk_factors = {}
    risk_score = 0.0
    
    # FACTOR 1: User-based risk scores
    if buyer:
        buyer_risk, buyer_factors = calculate_user_risk_score(buyer)
        risk_factors["buyer_risk"] = buyer_risk
        risk_factors["buyer_factors"] = buyer_factors
        risk_score += buyer_risk * 0.4  # 40% weight
    
    if seller:
        seller_risk, seller_factors = calculate_user_risk_score(seller)
        risk_factors["seller_risk"] = seller_risk
        risk_factors["seller_factors"] = seller_factors
        risk_score += seller_risk * 0.4  # 40% weight
    
    # FACTOR 2: New user risk
    if buyer:
        days_old = (datetime.utcnow() - buyer.created_at).days
        if days_old < 30:
            new_user_risk = 20 * (1 - (days_old / 30))  # Max 20 points
            risk_factors["new_user_buyer"] = round(new_user_risk, 2)
            risk_score += new_user_risk * 0.15  # 15% weight
    
    if seller:
        days_old = (datetime.utcnow() - seller.created_at).days
        if days_old < 30:
            new_user_risk = 20 * (1 - (days_old / 30))  # Max 20 points
            risk_factors["new_user_seller"] = round(new_user_risk, 2)
            risk_score += new_user_risk * 0.15  # 15% weight
    
    # FACTOR 3: Transaction amount vs history
    if buyer:
        buyer_transactions = session.exec(
            select(TradeTransaction).where(
                (TradeTransaction.buyer_id == buyer.id) |
                (TradeTransaction.seller_id == buyer.id)
            )
        ).all()
        
        if buyer_transactions:
            avg_transaction = sum(t.amount for t in buyer_transactions) / len(buyer_transactions)
            if amount > avg_transaction * 2:  # 2x average
                amount_risk = 15
                risk_factors["high_amount_buyer"] = amount_risk
                risk_score += amount_risk * 0.1  # 10% weight
        else:
            # First transaction - small additional risk
            unknown_history_risk = 5
            risk_factors["unknown_history_buyer"] = unknown_history_risk
            risk_score += unknown_history_risk * 0.1
    
    # FACTOR 4: Counterparty compliance
    if seller and seller.role == UserRole.BANK:
        risk_score *= 0.95  # 5% reduction if seller is a bank
        risk_factors["bank_seller_discount"] = -2.5
    
    # Normalize to 0-100
    risk_score = min(100.0, max(0.0, risk_score))
    
    return round(risk_score, 2), risk_factors



def get_risk_level(score: float) -> str:
    """Convert numerical score to risk level"""
    if score < 20:
        return "LOW"
    elif score < 40:
        return "MEDIUM"
    elif score < 60:
        return "HIGH"
    else:
        return "CRITICAL"
