from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlmodel import Session, select
import hashlib
import os
from datetime import datetime

from ..db import get_session
from ..models import (
    Document,
    LedgerEntry,
    DocumentStatus,
    DocumentType,
    TradeTransaction,
    User,
)
from ..dependencies.auth import get_current_user
from ..rules.document_rules import validate_transition, get_allowed_actions

router = APIRouter(prefix="/documents", tags=["Documents"])

FILES_DIR = "uploaded_files"
os.makedirs(FILES_DIR, exist_ok=True)


# -------------------------
# LIST DOCUMENTS
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
# CREATE DOCUMENT (STRICT WORKFLOW LINKED)
# -------------------------
@router.post("/")
async def create_document(
    doc_type: DocumentType = Form(...),
    doc_number: str = Form(...),
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # Validate transaction exists
    transaction = session.get(TradeTransaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Invalid transaction")

    # Read file
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    filepath = os.path.join(FILES_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    # Create document (STRICTLY LINKED TO TRANSACTION)
    document = Document(
        doc_type=doc_type,
        doc_number=doc_number,
        owner_id=user_id,
        transaction_id=transaction_id,
        file_url=filename,
        hash=file_hash,
        status=DocumentStatus.ISSUED,
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    # Ledger entry
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=user_id,
        action=DocumentStatus.ISSUED.value,
        meta={
            "transaction_id": transaction_id,
            "filename": file.filename,
            "hash": file_hash,
        },
    )

    session.add(ledger)
    session.commit()

    return {
        "id": document.id,
        "doc_type": document.doc_type,
        "doc_number": document.doc_number,
        "status": document.status,
        "transaction_id": transaction_id,
        "hash": file_hash,
    }


# -------------------------
# DOCUMENT DETAILS
# -------------------------
@router.get("/{doc_id}")
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
        "document": document,
        "ledger": ledger_entries,
    }


# -------------------------
# DOCUMENT ACTION
# -------------------------
@router.post("/{doc_id}/action")
def perform_action(
    doc_id: int,
    action: DocumentStatus,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    role = current_user["role"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    validate_transition(role, document.status, action)

    document.status = action
    session.add(document)

    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=action.value,
        meta={"transaction_id": document.transaction_id},
    )

    session.add(ledger)
    session.commit()

    return {
        "message": "Action recorded",
        "new_status": action.value,
    }


# -------------------------
# DOWNLOAD FILE
# -------------------------
@router.get("/{doc_id}/file")
def download_file(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    filepath = os.path.join(FILES_DIR, document.file_url)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath, filename=document.file_url)


# -------------------------
# VERIFY HASH INTEGRITY
# -------------------------
@router.post("/{doc_id}/verify")
def verify_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    filepath = os.path.join(FILES_DIR, document.file_url)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    with open(filepath, "rb") as f:
        content = f.read()

    computed_hash = hashlib.sha256(content).hexdigest()
    is_valid = computed_hash == document.hash

    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=DocumentStatus.VERIFIED.value,
        meta={
            "verification_result": "PASSED" if is_valid else "FAILED",
            "transaction_id": document.transaction_id,
        },
    )

    session.add(ledger)
    session.commit()

    return {
        "document_id": doc_id,
        "is_valid": is_valid,
        "stored_hash": document.hash,
        "computed_hash": computed_hash,
    }


# -------------------------
# GET FULL LEDGER
# -------------------------
@router.get("/ledger/all")
def get_all_ledger(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]
    user_id = current_user["user_id"]

    query = select(LedgerEntry).join(Document)

    if role != "ADMIN":
        query = query.where(Document.owner_id == user_id)

    entries = session.exec(query.order_by(LedgerEntry.id.desc())).all()

    return {
        "total": len(entries),
        "entries": entries,
    }
