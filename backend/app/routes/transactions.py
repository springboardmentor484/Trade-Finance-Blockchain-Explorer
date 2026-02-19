from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from ..db import get_session
from ..models import TradeTransaction, TransactionStatus, User
from ..schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionDetailResponse,
)
from ..rules.transaction_rules import calculate_risk_score, get_risk_level
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# -------------------------
# LIST TRANSACTIONS
# -------------------------
@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all transactions (admins see all, others see their own)
    """
    user_id = current_user["user_id"]
    role = current_user["role"]

    if role == "admin":
        # Admins see all transactions
        transactions = session.exec(select(TradeTransaction)).all()
    else:
        # Others see transactions where they are buyer, seller, or LC issuer
        transactions = session.exec(
            select(TradeTransaction).where(
                (TradeTransaction.buyer_id == user_id)
                | (TradeTransaction.seller_id == user_id)
                | (TradeTransaction.lc_issuer_id == user_id)
            )
        ).all()

    return transactions


# -------------------------
# CREATE TRANSACTION
# -------------------------
@router.post("/", response_model=TransactionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new trade transaction with automatic risk scoring
    Only admins or the buyer can initiate transactions
    """
    user_id = current_user["user_id"]
    role = current_user["role"]

    # Authorization: Must be admin or the buyer
    if role != "admin" and user_id != data.buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers or admins can initiate transactions"
        )

    # Validate users exist
    buyer = session.get(User, data.buyer_id)
    seller = session.get(User, data.seller_id)

    if not buyer or not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer or seller not found"
        )

    if data.lc_issuer_id:
        lc_issuer = session.get(User, data.lc_issuer_id)
        if not lc_issuer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LC issuer not found"
            )

    # Calculate risk score
    risk_score, risk_factors = calculate_risk_score(
        buyer, seller, data.amount, session
    )

    # Create transaction
    transaction = TradeTransaction(
        buyer_id=data.buyer_id,
        seller_id=data.seller_id,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        lc_number=data.lc_number,
        lc_issuer_id=data.lc_issuer_id,
        risk_score=risk_score,
        risk_factors=risk_factors,
        status=TransactionStatus.PENDING,
    )

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction


# -------------------------
# GET TRANSACTION DETAILS
# -------------------------
@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get detailed transaction information with risk factors"""
    user_id = current_user["user_id"]
    role = current_user["role"]

    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Authorization: Involved parties or admins
    if (
        role != "admin"
        and user_id not in [transaction.buyer_id, transaction.seller_id, transaction.lc_issuer_id]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this transaction"
        )

    return transaction


# -------------------------
# UPDATE TRANSACTION STATUS
# -------------------------
@router.post("/{transaction_id}/status", response_model=TransactionDetailResponse)
def update_transaction_status(
    transaction_id: int,
    data: TransactionUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Update transaction status (PENDING → IN_PROGRESS → COMPLETED → DISPUTED → CANCELLED)"""
    user_id = current_user["user_id"]
    role = current_user["role"]

    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Authorization: Involved parties or admins can update
    if (
        role != "admin"
        and user_id not in [transaction.buyer_id, transaction.seller_id, transaction.lc_issuer_id]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transaction"
        )

    # Validate status transition
    valid_statuses = [s.value for s in TransactionStatus]
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    transaction.status = data.status
    transaction.updated_at = datetime.utcnow()

    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return transaction


# -------------------------
# GET RISK ANALYTICS
# -------------------------
@router.get("/analytics/risk-summary")
def get_risk_summary(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Get risk summary for current user's transactions
    - Average risk score
    - Risk distribution
    - High-risk transactions
    """
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
            "user_id": user_id,
            "total_transactions": 0,
            "average_risk_score": 0.0,
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "high_risk_count": 0,
            "total_volume": 0.0,
        }

    # Calculate analytics
    avg_risk = sum(t.risk_score for t in transactions) / len(transactions)

    risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for t in transactions:
        level = get_risk_level(t.risk_score)
        risk_dist[level] += 1

    high_risk_count = sum(1 for t in transactions if t.risk_score >= 60)
    total_volume = sum(t.amount for t in transactions)

    return {
        "user_id": user_id,
        "total_transactions": len(transactions),
        "average_risk_score": round(avg_risk, 2),
        "risk_distribution": risk_dist,
        "high_risk_count": high_risk_count,
        "total_volume": total_volume,
    }

# -------------------------
# TRADE TRANSACTION FLOW (7 STEPS)
# -------------------------

@router.post("/{transaction_id}/step/create-po")
def step1_create_po(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    STEP 1: Buyer creates a PO
    Transaction is created with status = PENDING
    Ledger entry with status = ISSUED
    """
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Only buyer can create PO
    if role != "admin" and user_id != transaction.buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyer can create PO"
        )
    
    # Update transaction status to PENDING
    transaction.status = TransactionStatus.PENDING
    transaction.updated_at = datetime.utcnow()
    
    session.add(transaction)
    session.commit()
    
    # Create ledger entry
    from ..models import LedgerEntry
    ledger = LedgerEntry(
        document_id=None,  # Will be linked when document is created
        actor_id=user_id,
        action="PO_CREATED",
        meta={
            "transaction_id": transaction.id,
            "amount": transaction.amount,
            "seller_id": transaction.seller_id,
            "currency": transaction.currency,
        },
    )
    session.add(ledger)
    session.commit()
    
    return {
        "message": "PO created successfully",
        "transaction_id": transaction.id,
        "status": transaction.status.value,
    }


@router.post("/{transaction_id}/step/issue-loc")
def step2_issue_loc(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    STEP 2: Bank issues a LOC (Letter of Credit)
    Transaction must be in PENDING status
    """
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status != TransactionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction must be in PENDING status, currently {transaction.status.value}"
        )
    
    # Only bank can issue LOC
    if role != "admin" and role != "bank":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only bank can issue LOC"
        )
    
    # Update transaction with LC issuer
    transaction.lc_issuer_id = user_id
    transaction.updated_at = datetime.utcnow()
    
    session.add(transaction)
    session.commit()
    
    # Create ledger entry
    from ..models import LedgerEntry
    ledger = LedgerEntry(
        document_id=None,
        actor_id=user_id,
        action="LOC_ISSUED",
        meta={
            "transaction_id": transaction.id,
            "bank_id": user_id,
        },
    )
    session.add(ledger)
    session.commit()
    
    return {
        "message": "LOC issued successfully",
        "transaction_id": transaction.id,
        "lc_issuer_id": transaction.lc_issuer_id,
    }


@router.post("/{transaction_id}/step/verify")
def step3_verify(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    STEP 3: Auditor verifies PO and LOC
    Transitions transaction from PENDING to IN_PROGRESS
    """
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status != TransactionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction must be in PENDING status"
        )
    
    # Only auditor or admin can verify
    if role != "admin" and role != "auditor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only auditor can verify"
        )
    
    # Update transaction status to IN_PROGRESS
    transaction.status = TransactionStatus.IN_PROGRESS
    transaction.updated_at = datetime.utcnow()
    
    session.add(transaction)
    session.commit()
    
    # Create ledger entry
    from ..models import LedgerEntry
    ledger = LedgerEntry(
        document_id=None,
        actor_id=user_id,
        action="VERIFIED",
        meta={
            "transaction_id": transaction.id,
            "auditor_id": user_id,
        },
    )
    session.add(ledger)
    session.commit()
    
    return {
        "message": "Transaction verified successfully",
        "transaction_id": transaction.id,
        "status": transaction.status.value,
    }


@router.post("/{transaction_id}/step/mark-completed")
def step7_mark_completed(
    transaction_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    STEP 7: Bank pays the invoice
    Transitions transaction to COMPLETED
    Updates buyer and seller success counts
    """
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status != TransactionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction must be in IN_PROGRESS status"
        )
    
    # Only bank or related party can mark as completed
    if role != "admin" and user_id != transaction.lc_issuer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only issuing bank can mark as completed"
        )
    
    # Update transaction status
    transaction.status = TransactionStatus.COMPLETED
    transaction.updated_at = datetime.utcnow()
    
    # Update user success counts
    buyer = session.get(User, transaction.buyer_id)
    seller = session.get(User, transaction.seller_id)
    
    if buyer:
        buyer.completed_transactions += 1
        session.add(buyer)
    
    if seller:
        seller.completed_transactions += 1
        session.add(seller)
    
    session.add(transaction)
    session.commit()
    
    # Create ledger entry
    from ..models import LedgerEntry
    ledger = LedgerEntry(
        document_id=None,
        actor_id=user_id,
        action="COMPLETED",
        meta={
            "transaction_id": transaction.id,
            "bank_id": user_id,
        },
    )
    session.add(ledger)
    session.commit()
    
    return {
        "message": "Transaction completed successfully",
        "transaction_id": transaction.id,
        "status": transaction.status.value,
    }


@router.post("/{transaction_id}/mark-disputed")
def mark_disputed(
    transaction_id: int,
    reason: str = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Mark a transaction as disputed"""
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Only involved parties or admin can mark as disputed
    if (
        role != "admin"
        and user_id not in [transaction.buyer_id, transaction.seller_id]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark as disputed"
        )
    
    transaction.status = TransactionStatus.DISPUTED
    transaction.updated_at = datetime.utcnow()
    
    # Update user disputed counts
    buyer = session.get(User, transaction.buyer_id)
    seller = session.get(User, transaction.seller_id)
    
    if buyer:
        buyer.disputed_transactions += 1
        session.add(buyer)
    
    if seller:
        seller.disputed_transactions += 1
        session.add(seller)
    
    session.add(transaction)
    session.commit()
    
    # Create ledger entry
    from ..models import LedgerEntry
    ledger = LedgerEntry(
        document_id=None,
        actor_id=user_id,
        action="DISPUTED",
        meta={
            "transaction_id": transaction.id,
            "reason": reason or "Not specified",
        },
    )
    session.add(ledger)
    session.commit()
    
    return {
        "message": "Transaction marked as disputed",
        "transaction_id": transaction.id,
        "status": transaction.status.value,
    }