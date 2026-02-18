from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database import get_session
from app.models import User, TradeTransaction, TransactionStatusEnum, Document, RoleEnum
from app.auth.security import verify_token

router = APIRouter(prefix="/trades", tags=["trades"])


class TradeFlowRequest(BaseModel):
    """Start a new trade flow"""
    buyer_id: int
    seller_id: int
    amount: float
    currency: str = "USD"


class TradeFlowResponse(BaseModel):
    """Trade flow response"""
    transaction_id: int
    status: str
    message: str


def get_current_user(authorization: str, session: Session):
    """Extract and validate current user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token_data = verify_token(token)
    if not token_data or token_data.token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/initiate", response_model=TradeFlowResponse, summary="Initiate trade flow")
def initiate_trade_flow(
    payload: TradeFlowRequest,
    authorization: str = None,
    session: Session = Depends(get_session)
):
    """
    Initiate a new trade flow (PO creation)
    
    Step 1: Create transaction and initial PO document
    """
    
    current_user = get_current_user(authorization, session)
    
    # Validate users
    buyer = session.exec(select(User).where(User.id == payload.buyer_id)).first()
    seller = session.exec(select(User).where(User.id == payload.seller_id)).first()
    
    if not buyer or not seller:
        raise HTTPException(status_code=404, detail="Buyer or seller not found")
    
    # Create transaction
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    transaction_number = f"TX-{payload.buyer_id}-{payload.seller_id}-{timestamp}"
    
    transaction = TradeTransaction(
        transaction_number=transaction_number,
        buyer_id=payload.buyer_id,
        seller_id=payload.seller_id,
        amount=payload.amount,
        currency=payload.currency,
        status=TransactionStatusEnum.PENDING
    )
    
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return TradeFlowResponse(
        transaction_id=transaction.id,
        status=TransactionStatusEnum.PENDING.value,
        message="Trade flow initiated. Please upload PO document."
    )


@router.get("/{tx_id}/status", summary="Get trade flow status")
def get_trade_status(
    tx_id: int,
    session: Session = Depends(get_session)
):
    """Get current trade flow status"""
    
    transaction = session.exec(
        select(TradeTransaction).where(TradeTransaction.id == tx_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "transaction_id": transaction.id,
        "transaction_number": transaction.transaction_number,
        "current_status": transaction.status.value,
        "buyer_id": transaction.buyer_id,
        "seller_id": transaction.seller_id,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "steps_completed": {
            "po_created": bool(transaction.po_doc_id),
            "loc_issued": bool(transaction.loc_doc_id),
            "verified": transaction.status == TransactionStatusEnum.IN_PROGRESS,
            "bol_shipped": bool(transaction.bol_doc_id),
            "invoice_created": bool(transaction.invoice_doc_id),
            "completed": transaction.status == TransactionStatusEnum.COMPLETED
        },
        "created_at": transaction.created_at.isoformat(),
        "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None
    }
