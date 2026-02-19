from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from ..security.permission import require_action
from ..security.role_matrix import Action

from ..db import get_session
from ..models import (
    TradeTransaction,
    TransactionStatus,
    User,
    LedgerEntry,
    RiskScore,
    UserRole,
)
from ..schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionDetailResponse,
)
from ..rules.transaction_rules import calculate_risk_score, get_risk_level

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# =====================================================
# STATE MACHINE (STRICT TRANSITION CONTROL)
# =====================================================

VALID_TRANSITIONS = {
    TransactionStatus.PENDING: [TransactionStatus.IN_PROGRESS, TransactionStatus.CANCELLED],
    TransactionStatus.IN_PROGRESS: [TransactionStatus.COMPLETED, TransactionStatus.DISPUTED],
    TransactionStatus.DISPUTED: [TransactionStatus.COMPLETED],
    TransactionStatus.COMPLETED: [],
    TransactionStatus.CANCELLED: [],
}


def validate_transition(current: TransactionStatus, new: TransactionStatus):
    if new not in VALID_TRANSITIONS[current]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state transition: {current.value} → {new.value}",
        )


# =====================================================
# LIST TRANSACTIONS
# =====================================================

@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.VIEW_TRANSACTION)),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    if role == UserRole.ADMIN.value:
        return session.exec(select(TradeTransaction)).all()

    return session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()


# =====================================================
# CREATE TRANSACTION
# =====================================================

@router.post("/", response_model=TransactionDetailResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.CREATE_TRANSACTION)),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    if role != UserRole.ADMIN.value and user_id != data.buyer_id:
        raise HTTPException(status_code=403, detail="Only buyer or admin can create")

    buyer = session.get(User, data.buyer_id)
    seller = session.get(User, data.seller_id)

    if not buyer or not seller:
        raise HTTPException(status_code=404, detail="Buyer or seller not found")

    risk_score, risk_factors = calculate_risk_score(
        buyer, seller, data.amount, session
    )

    transaction = TradeTransaction(
        buyer_id=data.buyer_id,
        seller_id=data.seller_id,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        lc_number=data.lc_number,
        lc_issuer_id=data.lc_issuer_id,
        status=TransactionStatus.PENDING,
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    # Persist RiskScore table
    risk_record = RiskScore(
        transaction_id=transaction.id,
        score=risk_score,
        factors=risk_factors,
    )
    session.add(risk_record)

    # Ledger entry
    ledger = LedgerEntry(
        document_id=0,
        actor_id=user_id,
        action="TRANSACTION_CREATED",
        meta={"transaction_id": transaction.id},
    )
    session.add(ledger)

    session.commit()

    return transaction


# =====================================================
# UPDATE STATUS (STRICT STATE MACHINE)
# =====================================================

@router.post("/{transaction_id}/status", response_model=TransactionDetailResponse)
def update_status(
    transaction_id: int,
    data: TransactionUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.UPDATE_TRANSACTION_STATUS)),
):
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    new_status = TransactionStatus(data.status)

    # Store old status BEFORE change
    old_status = transaction.status

    validate_transition(old_status, new_status)

    transaction.status = new_status
    transaction.updated_at = datetime.utcnow()

    session.add(transaction)

    ledger = LedgerEntry(
        document_id=0,
        actor_id=current_user["user_id"],
        action="STATUS_CHANGED",
        meta={
            "transaction_id": transaction.id,
            "from": old_status.value,
            "to": new_status.value,
        },
    )
    session.add(ledger)

    session.commit()
    session.refresh(transaction)

    return transaction


# =====================================================
# RISK ANALYTICS
# =====================================================

@router.get("/analytics/risk-summary")
def get_risk_summary(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_action(Action.VIEW_ANALYTICS)),
):
    user_id = current_user["user_id"]

    transactions = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.buyer_id == user_id)
            | (TradeTransaction.seller_id == user_id)
            | (TradeTransaction.lc_issuer_id == user_id)
        )
    ).all()

    if not transactions:
        return {
            "total_transactions": 0,
            "average_risk_score": 0,
            "distribution": {},
        }

    risk_records = session.exec(
        select(RiskScore).where(
            RiskScore.transaction_id.in_([t.id for t in transactions])
        )
    ).all()

    if not risk_records:
        return {
            "total_transactions": len(transactions),
            "average_risk_score": 0,
            "distribution": {},
        }

    avg = sum(r.score for r in risk_records) / len(risk_records)

    distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for r in risk_records:
        distribution[get_risk_level(r.score)] += 1

    return {
        "total_transactions": len(transactions),
        "average_risk_score": round(avg, 2),
        "distribution": distribution,
    }
