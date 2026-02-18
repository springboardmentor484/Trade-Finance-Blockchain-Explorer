from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Document, LedgerEntry, User, DocumentTypeEnum, LedgerActionEnum, RoleEnum
from app.auth.security import verify_token, hash_sha256
from pydantic import BaseModel
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["documents"])

# Ensure files directory exists
os.makedirs("files", exist_ok=True)


class UploadResponse(BaseModel):
    """Document upload response"""
    id: int
    doc_number: str
    doc_type: str
    file_hash: str
    file_url: str


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


@router.post("/upload", response_model=UploadResponse, summary="Upload document")
def upload_document(
    doc_number: str = Form(...),
    doc_type: str = Form(...),
    seller_id: int = Form(...),
    file: UploadFile = File(...),
    authorization: str = None,
    session: Session = Depends(get_session)
):
    """
    Upload a document with SHA-256 hashing
    
    - **doc_number**: Document reference number (PO, BOL, LOC, etc.)
    - **doc_type**: Type of document (PO, BOL, LOC, INVOICE, COO, INSURANCE_CERT)
    - **seller_id**: ID of seller/supplier
    - **file**: The document file to upload
    """
    # Validate current user
    current_user = get_current_user(authorization, session)
    
    # Validate document type
    try:
        doc_type_enum = DocumentTypeEnum(doc_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document type. Valid types: {', '.join([e.value for e in DocumentTypeEnum])}"
        )
    
    # Validate seller exists
    seller = session.exec(select(User).where(User.id == seller_id)).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Check if document already exists
    existing = session.exec(
        select(Document).where(Document.doc_number == doc_number)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document number already exists")
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"files/{doc_number}{file_extension}"
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Calculate SHA-256 hash
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            file_hash = hash_sha256(file_content)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to hash file: {str(e)}")
    
    # Create document record
    document = Document(
        doc_number=doc_number,
        doc_type=doc_type_enum,
        owner_id=current_user.id,
        file_url=file_path,
        file_hash=file_hash,
        metadata={
            "seller_id": seller_id,
            "uploaded_by": current_user.name,
            "file_name": file.filename
        }
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    # Create initial ledger entry
    ledger_entry = LedgerEntry(
        document_id=document.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        action=LedgerActionEnum.ISSUED,
        metadata={"seller_id": seller_id}
    )
    
    session.add(ledger_entry)
    session.commit()
    
    return UploadResponse(
        id=document.id,
        doc_number=document.doc_number,
        doc_type=document.doc_type.value,
        file_hash=file_hash,
        file_url=file_path
    )


@router.post("/verify-hash", summary="Verify document hash")
def verify_hash(
    doc_id: int,
    file_hash: str = Form(...),
    session: Session = Depends(get_session)
):
    """Verify the SHA-256 hash of a document"""
    document = session.exec(
        select(Document).where(Document.id == doc_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    is_valid = document.file_hash == file_hash
    
    return {
        "doc_id": doc_id,
        "stored_hash": document.file_hash,
        "provided_hash": file_hash,
        "is_valid": is_valid,
        "status": "tamper_proof" if is_valid else "tamper_detected"
    }

