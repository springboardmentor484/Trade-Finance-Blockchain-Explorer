from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
import os

from app.auth.security import verify_token, hash_sha256
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import Document, LedgerEntry, User
from app.database import get_session

router = APIRouter(tags=["documents"])

# Response models for nice Swagger schemas
class DocumentOut(BaseModel):
    id: int
    doc_number: str
    doc_type: str
    file_url: Optional[str] = None
    file_hash: Optional[str] = None
    created_at: Optional[datetime] = None

class LedgerEntryOut(BaseModel):
    actor_role: str
    action: str
    additional_metadata: Optional[dict] = None
    created_at: Optional[datetime] = None

class DocumentWithLedger(BaseModel):
    document: DocumentOut
    ledger: List[LedgerEntryOut] = []

class DocumentsListResponse(BaseModel):
    documents: List[DocumentOut]
    total: int

class ActionRequest(BaseModel):
    doc_id: int
    action: str

security = HTTPBearer()

def require_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token_data = verify_token(creds.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"user_id": token_data.user_id, "role": token_data.role, "email": token_data.email}

@router.post("/documents/upload", summary="Upload Document", response_model=DocumentOut)
def upload_document(
    doc_number: str = Form(...),
    doc_type: str = Form(...),
    seller_id: int = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(require_token),
    session: Session = Depends(get_session)
):
    """Upload a document with SHA-256 hash"""
    try:
        # Create files directory if it doesn't exist
        os.makedirs("backend/files", exist_ok=True)
        
        # Read file and hash it
        file_content = file.file.read()
        file_hash = hash_sha256(file_content)
        
        # Save file to disk
        filename = f"backend/files/{doc_number}_{file.filename}"
        with open(filename, "wb") as f:
            f.write(file_content)
        
        # Check if doc_number already exists
        existing = session.exec(select(Document).where(Document.doc_number == doc_number)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Document number already exists")
        
        # Create document in database
        doc = Document(
            doc_number=doc_number,
            doc_type=doc_type,
            owner_id=current_user["user_id"],
            file_url=filename,
            file_hash=file_hash,
            hash_algorithm="SHA256",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(doc)
        session.flush()  # Get the ID before commit
        doc_id = doc.id
        
        # Create ledger entry for ISSUED action
        ledger = LedgerEntry(
            document_id=doc_id,
            actor_id=current_user["user_id"],
            actor_role=current_user["role"],
            action="ISSUED",
            additional_metadata={"seller_id": seller_id, "file_hash": file_hash},
            created_at=datetime.utcnow()
        )
        session.add(ledger)
        session.commit()
        
        return DocumentOut(
            id=doc.id,
            doc_number=doc.doc_number,
            doc_type=doc.doc_type,
            file_url=doc.file_url,
            file_hash=doc.file_hash,
            created_at=doc.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents/documents", summary="List Documents")
def list_documents(
    current_user = Depends(require_token),
    session: Session = Depends(get_session),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """List all documents the user has access to"""
    try:
        # Get all documents (or filter by owner for corporate users)
        statement = select(Document).offset(skip).limit(limit)
        documents = session.exec(statement).all()
        
        # Get total count
        total_stmt = select(Document)
        total = session.exec(total_stmt).all()
        
        return {
            "documents": [
                {
                    "id": doc.id,
                    "doc_number": doc.doc_number,
                    "doc_type": doc.doc_type,
                    "file_url": doc.file_url,
                    "file_hash": doc.file_hash,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in documents
            ],
            "total": len(total)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@router.get("/documents/{doc_id}", summary="Get Document", response_model=DocumentWithLedger)
def get_document(
    doc_id: int,
    current_user = Depends(require_token),
    session: Session = Depends(get_session)
):
    """Get document with complete ledger trail"""
    try:
        doc = session.exec(select(Document).where(Document.id == doc_id)).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        ledger = session.exec(select(LedgerEntry).where(LedgerEntry.document_id == doc_id)).all()
        
        return DocumentWithLedger(
            document=DocumentOut(
                id=doc.id,
                doc_number=doc.doc_number,
                doc_type=doc.doc_type,
                file_url=doc.file_url,
                file_hash=doc.file_hash,
                created_at=doc.created_at
            ),
            ledger=[
                LedgerEntryOut(
                    actor_role=entry.actor_role,
                    action=entry.action,
                    additional_metadata=entry.additional_metadata,
                    created_at=entry.created_at
                )
                for entry in ledger
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")

@router.get("/documents/file/{doc_id}", summary="Download Document File")
def get_file(
    doc_id: int,
    current_user = Depends(require_token),
    session: Session = Depends(get_session)
):
    """Download document file"""
    try:
        doc = session.exec(select(Document).where(Document.id == doc_id)).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not os.path.exists(doc.file_url):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        with open(doc.file_url, "rb") as f:
            data = f.read()
        
        return {
            "file_url": doc.file_url,
            "doc_number": doc.doc_number,
            "size": len(data),
            "file_hash": doc.file_hash
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch file: {str(e)}")

@router.post("/documents/action", summary="Perform Action on Document")
def perform_action(
    payload: ActionRequest,
    current_user = Depends(require_token),
    session: Session = Depends(get_session)
):
    """Perform an action (VERIFY, SHIP, RECEIVE, PAY, etc.) on a document"""
    try:
        doc = session.exec(select(Document).where(Document.id == payload.doc_id)).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create ledger entry for action
        entry = LedgerEntry(
            document_id=payload.doc_id,
            actor_id=current_user["user_id"],
            actor_role=current_user["role"],
            action=payload.action,
            additional_metadata={"timestamp": datetime.utcnow().isoformat()},
            created_at=datetime.utcnow()
        )
        session.add(entry)
        session.commit()
        
        return {
            "status": "ok",
            "doc_id": payload.doc_id,
            "action": payload.action,
            "actor_id": current_user["user_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to perform action: {str(e)}")

