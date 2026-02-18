from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import TradeTransaction, TransactionStatus , User
from backend.utils import get_current_user
from datetime import datetime

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/")
def create_transaction(
    seller_id: int,
    amount: float,
    currency: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    transaction = TradeTransaction(
        buyer_id=current_user.id,
        seller_id=seller_id,
        amount=amount,
        currency=currency.upper(),
        status=TransactionStatus.pending,
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction

@router.get("/")
def get_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(TradeTransaction)).all()

@router.put("/{transaction_id}/status")
def update_transaction_status(
    transaction_id: int,
    new_status: TransactionStatus,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    tx = session.get(TradeTransaction, transaction_id)

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.status = new_status
    tx.updated_at = datetime.utcnow()

    session.add(tx)
    session.commit()
    session.refresh(tx)  
    return tx