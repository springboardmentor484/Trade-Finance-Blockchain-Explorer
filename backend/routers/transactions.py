from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import TradeTransaction, TransactionStatus , User
from backend.utils import get_current_user
from datetime import datetime
from datetime import datetime, timedelta
from fastapi import HTTPException

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

VALID_TRANSITIONS = {
    TransactionStatus.pending: [TransactionStatus.in_progress],
    TransactionStatus.in_progress: [
        TransactionStatus.completed,
        TransactionStatus.disputed,
    ],
    TransactionStatus.completed: [],
    TransactionStatus.disputed: [],
}

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

    #  Save old status BEFORE changing
    old_status = tx.status

    # State Machine Validation
    if new_status not in VALID_TRANSITIONS[tx.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {tx.status} to {new_status}",
        )

    #  Role Control
    if new_status == TransactionStatus.in_progress:
        if current_user.id != tx.seller_id:
            raise HTTPException(403, "Only seller can start transaction")

    if new_status == TransactionStatus.completed:
        if current_user.id != tx.buyer_id:
            raise HTTPException(403, "Only buyer can complete transaction")

    if new_status == TransactionStatus.disputed:
        if current_user.id not in [tx.buyer_id, tx.seller_id]:
            raise HTTPException(403, "Not allowed to dispute")

    # Update status
    tx.status = new_status
    tx.updated_at = datetime.utcnow()

    # Create Audit Record
    audit = TransactionAudit(
        transaction_id=tx.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
    )

    session.add(tx)
    session.add(audit)

    session.commit()
    session.refresh(tx)

    return tx

@router.post("/expire-pending")
def expire_pending_transactions(
    session: Session = Depends(get_session),
):
    three_days_ago = datetime.utcnow() - timedelta(days=3)

    pending_tx = session.exec(
        select(TradeTransaction).where(
            TradeTransaction.status == TransactionStatus.pending,
            TradeTransaction.created_at <= three_days_ago,
        )
    ).all()

    for tx in pending_tx:
        tx.status = TransactionStatus.expired
        tx.updated_at = datetime.utcnow()
        session.add(tx)

    session.commit()

    return {"expired_count": len(pending_tx)}
