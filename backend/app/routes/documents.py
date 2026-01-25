from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Document, LedgerEntry, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentAction
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
# CREATE DOCUMENT
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

    # Ledger entry on creation (MANDATORY)
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


# -------------------------
# GET DOCUMENT DETAILS
# -------------------------
@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    document = session.get(Document, doc_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


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

    next_status = DocumentStatus(payload.action)

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
        "new_status": next_status.value,
    }


# -------------------------
# DOCUMENT LEDGER
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
