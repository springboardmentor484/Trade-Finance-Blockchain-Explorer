from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import (
    Document,
    LedgerEntry,
    DocumentStatus,
    UserRole,
)
from app.schemas.document import DocumentCreate, DocumentAction
from app.rules.document_rules import validate_transition

router = APIRouter(prefix="/documents", tags=["Documents"])


# -------------------------
# CREATE / UPLOAD DOCUMENT
# -------------------------
@router.post("/")
def create_document(
    payload: DocumentCreate,
    user_id: int,
    session: Session = Depends(get_session),
):
    document = Document(
        doc_type=payload.doc_type,
        doc_number=payload.doc_number,
        owner_id=user_id,
        file_url=payload.file_url,
        hash=payload.hash,
        status=DocumentStatus.ISSUED,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=user_id,
        action=DocumentStatus.ISSUED,
        meta={"doc_type": document.doc_type},
    )
    session.add(ledger)
    session.commit()

    return {"id": document.id}


# -------------------------
# GET DOCUMENT
# -------------------------
@router.get("/{doc_id}")
def get_document(doc_id: int, session: Session = Depends(get_session)):
    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


# -------------------------
# DOCUMENT ACTION (WEEK 4 LOGIC)
# -------------------------
@router.post("/{doc_id}/action")
def perform_action(
    doc_id: int,
    payload: DocumentAction,
    user_id: int,
    session: Session = Depends(get_session),
):
    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # ⚠️ TEMPORARY (Week 5: extract from JWT)
    user_role = UserRole.BUYER

    try:
        next_status = DocumentStatus(payload.action)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid action/status")

    # 🔒 Enforce business rules
    try:
        validate_transition(
            role=user_role,
            current_status=document.status,
            next_status=next_status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ✅ Apply valid transition
    document.status = next_status
    session.add(document)

    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=next_status,
        meta=payload.meta,
    )
    session.add(ledger)

    session.commit()
    return {"status": "action recorded"}


# -------------------------
# DOCUMENT LEDGER (TIMELINE)
# -------------------------
@router.get("/{doc_id}/ledger")
def get_ledger(doc_id: int, session: Session = Depends(get_session)):
    entries = session.exec(
        select(LedgerEntry).where(LedgerEntry.document_id == doc_id)
    ).all()
    return entries
