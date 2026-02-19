from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
import hashlib
import os
from datetime import datetime

from ..db import get_session
from ..models import Document, LedgerEntry, DocumentStatus, DocumentType
from ..schemas.document import (
    DocumentCreate,
    DocumentAction,
    DocumentDetailResponse,
    DocumentReadResponse,
    AllowedActionsResponse,
)
from ..rules.document_rules import validate_transition, get_allowed_actions
from ..dependencies.auth import get_current_user

# Create files directory if it doesn't exist
FILES_DIR = "uploaded_files"
os.makedirs(FILES_DIR, exist_ok=True)

router = APIRouter(prefix="/documents", tags=["Documents"])


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
# CREATE DOCUMENT (with file upload)
# -------------------------
@router.post("/")
async def create_document(
    doc_type: DocumentType = Form(...),
    doc_number: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    
    # Read file content
    content = await file.read()
    
    # Compute SHA-256 hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    filepath = os.path.join(FILES_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Create document record
    document = Document(
        doc_type=doc_type,
        doc_number=doc_number,
        owner_id=user_id,
        file_url=filename,
        hash=file_hash,
        status=DocumentStatus.ISSUED,
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    # Create ledger entry
    ledger = LedgerEntry(
        document_id=document.id,
        actor_id=user_id,
        action=DocumentStatus.ISSUED.value,
        meta={"filename": file.filename, "size": len(content)},
    )
    
    session.add(ledger)
    session.commit()
    
    return {
        "id": document.id,
        "doc_type": document.doc_type.value,
        "doc_number": document.doc_number,
        "status": document.status.value,
        "hash": file_hash,
        "file_url": filename,
    }


# -------------------------
# DOCUMENT DETAILS
# -------------------------
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


# -------------------------
# SINGLE READ
# -------------------------
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


# -------------------------
# ALLOWED ACTIONS
# -------------------------
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

    if role != "admin" and document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    allowed_actions = get_allowed_actions(
        role=role,
        current_status=document.status,
    )

    return {
        "current_status": document.status,
        "allowed_actions": allowed_actions,
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
    from fastapi.responses import FileResponse
    
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
# VERIFY DOCUMENT INTEGRITY
# -------------------------
@router.post("/{doc_id}/verify")
def verify_document(
    doc_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Verify document integrity by recomputing hash"""
    user_id = current_user["user_id"]
    
    document = session.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Recompute hash
    filepath = os.path.join(FILES_DIR, document.file_url)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    with open(filepath, "rb") as f:
        content = f.read()
    computed_hash = hashlib.sha256(content).hexdigest()
    
    # Check if matches
    is_valid = computed_hash == document.hash
    
    # Create ledger entry recording verification
    ledger = LedgerEntry(
        document_id=doc_id,
        actor_id=user_id,
        action=DocumentStatus.VERIFIED.value,
        meta={
            "verification_result": "PASSED" if is_valid else "FAILED",
            "stored_hash": document.hash,
            "computed_hash": computed_hash,
        },
    )
    
    session.add(ledger)
    session.commit()
    
    return {
        "document_id": doc_id,
        "is_valid": is_valid,
        "stored_hash": document.hash,
        "computed_hash": computed_hash,
        "message": "Document integrity verified" if is_valid else "⚠️ Document has been tampered with!",
    }


# -------------------------
# GET FULL LEDGER (with filters)
# -------------------------
@router.get("/ledger/all")
def get_all_ledger(
    doc_id: int = None,
    action: str = None,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Fetch full ledger with optional filters"""
    user_id = current_user["user_id"]
    role = current_user["role"]
    
    query = select(LedgerEntry).join(Document)
    
    # Auth: only admins see all ledger, others see their own docs
    if role != "admin":
        query = query.where(Document.owner_id == user_id)
    
    # Filter by document if provided
    if doc_id:
        query = query.where(LedgerEntry.document_id == doc_id)
    
    # Filter by action if provided
    if action:
        query = query.where(LedgerEntry.action == action)
    
    entries = session.exec(
        query.order_by(LedgerEntry.id.desc())
    ).all()
    
    return {
        "total": len(entries),
        "entries": entries,
    }