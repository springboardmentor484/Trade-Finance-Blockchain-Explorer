from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Document, LedgerEntry, DocumentStatus
from app.schemas.document import (
    DocumentCreate,
    DocumentAction,
    DocumentDetailResponse,
    DocumentReadResponse,
    AllowedActionsResponse,
)
from app.rules.document_rules import validate_transition, get_allowed_actions
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
# DOCUMENT DETAILS (STEP 2.3)
# =========================================================
@router.get("/{doc_id}", response_model=DocumentDetailResponse)
def get_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    ledger_entries = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.id)
    ).all()

    return {
        "id": document.id,
        "doc_type": document.doc_type,
        "doc_number": document.doc_number,
        "status": document.status,
        "owner_id": document.owner_id,
        "ledger": ledger_entries,
    }


# -------------------------
# DOCUMENT ACTION (STEP 2.4 / 2.5)
# -------------------------
@router.post("/{doc_id}/action")
def perform_action(
    doc_id: int,
    payload: DocumentAction,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    validate_transition(
        role=role,
        current_status=document.status,
        next_status=payload.action,
    )

    document.status = payload.action
    session.add(document)

    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=payload.action.value,
        meta=payload.meta or {},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Action recorded",
        "document_id": doc_id,
        "new_status": payload.action.value,
    }


# -------------------------------------------------
# SINGLE-CALL DOCUMENT READ MODEL (STEP 2.8)
# -------------------------------------------------
@router.get("/{doc_id}/read", response_model=DocumentReadResponse)
def read_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if role != "admin" and document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    ledger_entries = session.exec(
        select(LedgerEntry)
        .where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.id)
    ).all()

    allowed_actions = get_allowed_actions(
        role=role,
        current_status=document.status,
    )

    return {
        "document": document,
        "ledger": ledger_entries,
        "allowed_actions": allowed_actions,
    }


# -------------------------------------------------
# STEP 2.9 — ALLOWED ACTIONS (UI DROPDOWNS)
# -------------------------------------------------
@router.get("/{doc_id}/allowed-actions", response_model=AllowedActionsResponse)
def get_document_allowed_actions(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # ✅ FIXED ACCESS RULE
    if role == "admin":
        pass
    elif document.owner_id == user_id:
        pass
    else:
        allowed = get_allowed_actions(
            role=role,
            current_status=document.status,
        )
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this document",
            )

    allowed_actions = get_allowed_actions(
        role=role,
        current_status=document.status,
    )

    return {
        "current_status": document.status,
        "allowed_actions": allowed_actions,
    }
