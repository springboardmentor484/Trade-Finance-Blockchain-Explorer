from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Document, LedgerEntry, DocumentStatus
from app.schemas.document import (
    DocumentCreate,
    DocumentAction,
    DocumentDetailResponse,
)
from app.rules.document_rules import validate_transition
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])


# -------------------------
# LIST DOCUMENTS (STEP 2.1)
# -------------------------
@router.get("/")
def list_documents(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    documents = session.exec(
        select(Document)
        .where(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
    ).all()

    return documents


# -------------------------
# CREATE DOCUMENT (STEP 2.2)
# -------------------------
@router.post("/")
def create_document(
    payload: DocumentCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

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

    # 🔒 Ledger entry on creation (MANDATORY)
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=user_id,
        action=DocumentStatus.ISSUED.value,
        meta={},
    )

    session.add(ledger)
    session.commit()

    return {
        "id": document.id,
        "status": document.status.value,
    }


# =========================================================
# 🔥 STEP 2.3.3 — DOCUMENT DETAILS (PRODUCTION API)
# =========================================================
@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    user_role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 🔒 Access rule: owner OR permitted role (extend later)
    if document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # 📜 Fetch ledger
    ledger_entries = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.id)
    ).all()

    # 🎯 Calculate allowed actions (business rules)
    allowed_actions = []
    for status in DocumentStatus:
        try:
            validate_transition(
                role=user_role,
                current_status=document.status,
                next_status=status,
            )
            allowed_actions.append(status)
        except Exception:
            continue

    return {
        "id": document.id,
        "doc_type": document.doc_type,
        "doc_number": document.doc_number,
        "status": document.status,
        "owner_id": document.owner_id,
        "ledger": ledger_entries,
        "allowed_actions": allowed_actions,
    }


# -------------------------
# DOCUMENT ACTION
# -------------------------
@router.post("/{doc_id}/action")
def perform_action(
    doc_id: int,
    payload: DocumentAction,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    user_role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    next_status = payload.action

    validate_transition(
        role=user_role,
        current_status=document.status,
        next_status=next_status,
    )

    document.status = next_status
    session.add(document)

    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=next_status.value,
        meta=payload.meta or {},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Action recorded",
        "document_id": doc_id,
        "new_status": next_status.value,
    }


# -------------------------
# DOCUMENT LEDGER (OPTIONAL)
# -------------------------
@router.get("/{doc_id}/ledger")
def get_ledger(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    entries = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.id)
    ).all()

    return entries
