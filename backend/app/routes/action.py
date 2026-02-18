from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.models import (
    Document, LedgerEntry, User, TradeTransaction,
    LedgerActionEnum, TransactionStatusEnum, RoleEnum
)
from app.auth.security import verify_token

router = APIRouter(prefix="/actions", tags=["actions"])


# Action permissions mapping
ACTION_PERMISSIONS = {
    ("bank", "BILL_OF_LADING"): ["RECEIVED"],
    ("corporate", "BILL_OF_LADING"): ["SHIPPED", "VERIFIED"],
    ("corporate", "PO"): ["ISSUED"],
    ("corporate", "INVOICE"): ["RECEIVED"],
    ("auditor", "PO"): ["VERIFIED"],
    ("auditor", "LOC"): ["VERIFIED"],
    ("bank", "INVOICE"): ["PAID"],
    ("bank", "LOC"): ["ISSUED"],
}


class ActionRequest(BaseModel):
    """Action request"""
    doc_id: int
    action: str


class ActionResponse(BaseModel):
    """Action response"""
    ledger_entry_id: int
    document_id: int
    action: str
    status: str


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


@router.post("/perform", response_model=ActionResponse, summary="Perform action on document")
def perform_action(
    payload: ActionRequest,
    authorization: str = None,
    session: Session = Depends(get_session)
):
    """
    Perform an action on a document based on role-based permissions
    
    Allowed actions:
    - bank + BILL_OF_LADING → RECEIVED
    - corporate + BILL_OF_LADING → SHIPPED, VERIFIED
    - corporate + PO → ISSUED
    - auditor + PO → VERIFIED
    - auditor + LOC → VERIFIED
    - bank + INVOICE → PAID
    - bank + LOC → ISSUED
    """
    
    # Validate current user
    current_user = get_current_user(authorization, session)
    
    # Fetch document
    document = session.exec(
        select(Document).where(Document.id == payload.doc_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    key = (current_user.role.value, document.doc_type.value)
    allowed_actions = ACTION_PERMISSIONS.get(key, [])
    
    if payload.action not in allowed_actions:
        raise HTTPException(
            status_code=403,
            detail=f"Action '{payload.action}' not allowed for {current_user.role.value} on {document.doc_type.value} documents"
        )
    
    # Create ledger entry
    try:
        action_enum = LedgerActionEnum(payload.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Valid actions: {', '.join([e.value for e in LedgerActionEnum])}"
        )
    
    ledger_entry = LedgerEntry(
        document_id=document.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        action=action_enum,
        metadata={"performed_by": current_user.name}
    )
    
    session.add(ledger_entry)
    session.commit()
    session.refresh(ledger_entry)
    
    # Update transaction status if applicable
    transaction = session.exec(
        select(TradeTransaction).where(
            (TradeTransaction.po_doc_id == document.id) |
            (TradeTransaction.loc_doc_id == document.id) |
            (TradeTransaction.bol_doc_id == document.id) |
            (TradeTransaction.invoice_doc_id == document.id)
        )
    ).first()
    
    if transaction:
        # Count verified documents
        verified_entries = session.exec(
            select(LedgerEntry).where(
                (LedgerEntry.action == LedgerActionEnum.VERIFIED),
                ((LedgerEntry.document_id == transaction.po_doc_id) |
                 (LedgerEntry.document_id == transaction.loc_doc_id))
            )
        ).all()
        
        if len(verified_entries) >= 2:  # Both PO and LOC verified
            transaction.status = TransactionStatusEnum.IN_PROGRESS
        
        if action_enum == LedgerActionEnum.PAID:
            transaction.status = TransactionStatusEnum.COMPLETED
            from datetime import datetime
            transaction.completed_at = datetime.utcnow()
        
        session.add(transaction)
        session.commit()
    
    return ActionResponse(
        ledger_entry_id=ledger_entry.id,
        document_id=document.id,
        action=action_enum.value,
        status="success"
    )


@router.get("/ledger/{doc_id}", summary="Get full ledger for document")
def get_ledger(
    doc_id: int,
    session: Session = Depends(get_session)
):
    """Get all ledger entries for a document"""
    
    document = session.exec(
        select(Document).where(Document.id == doc_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    entries = session.exec(
        select(LedgerEntry).where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.created_at.asc())
    ).all()
    
    return {
        "doc_id": doc_id,
        "doc_number": document.doc_number,
        "ledger_count": len(entries),
        "entries": [
            {
                "id": entry.id,
                "actor_id": entry.actor_id,
                "actor_role": entry.actor_role.value,
                "action": entry.action.value,
                "metadata": entry.metadata,
                "timestamp": entry.created_at.isoformat()
            }
            for entry in entries
        ]
    }

