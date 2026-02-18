from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_session
from app.models import (
    TradeTransaction, Document, User, TransactionStatusEnum,
    DocumentTypeEnum
)
from app.auth.security import verify_token

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionRequest(BaseModel):
    """Create transaction request"""
    buyer_id: int
    seller_id: int
    amount: float
    currency: str = "USD"
    po_doc_id: Optional[int] = None


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: int
    transaction_number: str
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    status: str
    created_at: str
    updated_at: str


class TransactionDetailResponse(TransactionResponse):
    """Transaction with document details"""
    po_doc: Optional[dict] = None
    loc_doc: Optional[dict] = None
    bol_doc: Optional[dict] = None
    invoice_doc: Optional[dict] = None


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


@router.post("/create", response_model=TransactionResponse, summary="Create new transaction")
def create_transaction(
    payload: TransactionRequest,
    authorization: str = None,
    session: Session = Depends(get_session)
):
    """
    Create a new trade transaction
    
    This initiates a trade flow with status = pending
    """
    
    # Validate current user is authorized
    current_user = get_current_user(authorization, session)
    
    # Validate buyer and seller exist
    buyer = session.exec(select(User).where(User.id == payload.buyer_id)).first()
    seller = session.exec(select(User).where(User.id == payload.seller_id)).first()
    
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Generate transaction number
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    transaction_number = f"TX-{payload.buyer_id}-{payload.seller_id}-{timestamp}"
    
    # Create transaction
    transaction = TradeTransaction(
        transaction_number=transaction_number,
        buyer_id=payload.buyer_id,
        seller_id=payload.seller_id,
        amount=payload.amount,
        currency=payload.currency,
        status=TransactionStatusEnum.PENDING,
        po_doc_id=payload.po_doc_id
    )
    
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return TransactionResponse(
        id=transaction.id,
        transaction_number=transaction.transaction_number,
        buyer_id=transaction.buyer_id,
        seller_id=transaction.seller_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.status.value,
        created_at=transaction.created_at.isoformat(),
        updated_at=transaction.updated_at.isoformat()
    )


@router.get("/{tx_id}", response_model=TransactionDetailResponse, summary="Get transaction details")
def get_transaction(
    tx_id: int,
    session: Session = Depends(get_session)
):
    """Get detailed transaction information with all related documents"""
    
    transaction = session.exec(
        select(TradeTransaction).where(TradeTransaction.id == tx_id)
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Fetch related documents
    po_doc = None
    loc_doc = None
    bol_doc = None
    invoice_doc = None
    
    if transaction.po_doc_id:
        doc = session.exec(select(Document).where(Document.id == transaction.po_doc_id)).first()
        if doc:
            po_doc = {"id": doc.id, "doc_number": doc.doc_number, "doc_type": doc.doc_type.value}
    
    if transaction.loc_doc_id:
        doc = session.exec(select(Document).where(Document.id == transaction.loc_doc_id)).first()
        if doc:
            loc_doc = {"id": doc.id, "doc_number": doc.doc_number, "doc_type": doc.doc_type.value}
    
    if transaction.bol_doc_id:
        doc = session.exec(select(Document).where(Document.id == transaction.bol_doc_id)).first()
        if doc:
            bol_doc = {"id": doc.id, "doc_number": doc.doc_number, "doc_type": doc.doc_type.value}
    
    if transaction.invoice_doc_id:
        doc = session.exec(select(Document).where(Document.id == transaction.invoice_doc_id)).first()
        if doc:
            invoice_doc = {"id": doc.id, "doc_number": doc.doc_number, "doc_type": doc.doc_type.value}
    
    return TransactionDetailResponse(
        id=transaction.id,
        transaction_number=transaction.transaction_number,
        buyer_id=transaction.buyer_id,
        seller_id=transaction.seller_id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.status.value,
        created_at=transaction.created_at.isoformat(),
        updated_at=transaction.updated_at.isoformat(),
        po_doc=po_doc,
        loc_doc=loc_doc,
        bol_doc=bol_doc,
        invoice_doc=invoice_doc
    )


@router.get("", summary="List transactions")
def list_transactions(
    status: Optional[str] = None,
    buyer_id: Optional[int] = None,
    seller_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """List transactions with optional filters"""
    
    query = select(TradeTransaction)
    
    if status:
        try:
            status_enum = TransactionStatusEnum(status)
            query = query.where(TradeTransaction.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if buyer_id:
        query = query.where(TradeTransaction.buyer_id == buyer_id)
    
    if seller_id:
        query = query.where(TradeTransaction.seller_id == seller_id)
    
    transactions = session.exec(
        query.order_by(TradeTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    # Count total
    count_query = select(TradeTransaction)
    if status:
        count_query = count_query.where(TradeTransaction.status == status_enum)
    if buyer_id:
        count_query = count_query.where(TradeTransaction.buyer_id == buyer_id)
    if seller_id:
        count_query = count_query.where(TradeTransaction.seller_id == seller_id)
    
    from sqlmodel import func
    total = session.exec(select(func.count(TradeTransaction.id)).select_from(count_query.subquery())).one()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": t.id,
                "transaction_number": t.transaction_number,
                "buyer_id": t.buyer_id,
                "seller_id": t.seller_id,
                "amount": t.amount,
                "currency": t.currency,
                "status": t.status.value,
                "created_at": t.created_at.isoformat()
            }
            for t in transactions
        ]
    }


@router.get("/stats/summary", summary="Get transaction statistics")
def get_transaction_stats(session: Session = Depends(get_session)):
    """Get transaction statistics and analytics"""
    
    from sqlmodel import func
    
    transactions = session.exec(select(TradeTransaction)).all()
    
    if not transactions:
        return {
            "total_transactions": 0,
            "total_amount": 0.0,
            "by_status": {},
            "by_currency": {}
        }
    
    # Count by status
    by_status = {}
    for status in TransactionStatusEnum:
        count = sum(1 for t in transactions if t.status == status)
        by_status[status.value] = count
    
    # Sum by currency
    by_currency = {}
    for t in transactions:
        if t.currency not in by_currency:
            by_currency[t.currency] = 0
        by_currency[t.currency] += t.amount
    
    total_amount = sum(t.amount for t in transactions)
    
    # Average completion time
    completed = [t for t in transactions if t.status == TransactionStatusEnum.COMPLETED and t.completed_at]
    avg_completion_time = None
    if completed:
        total_time = sum((t.completed_at - t.created_at).total_seconds() for t in completed)
        avg_completion_time = total_time / len(completed)
    
    return {
        "total_transactions": len(transactions),
        "total_amount": total_amount,
        "by_status": by_status,
        "by_currency": by_currency,
        "average_completion_time_seconds": avg_completion_time
    }
