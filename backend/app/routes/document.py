from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_session
from app.models import Document, LedgerEntry

router = APIRouter(prefix="/documents", tags=["documents"])


class LedgerEntryResponse(BaseModel):
    """Ledger entry response"""
    id: int
    document_id: int
    actor_id: int
    actor_role: str
    action: str
    metadata: dict
    created_at: str


class DocumentResponse(BaseModel):
    """Document response"""
    id: int
    doc_number: str
    doc_type: str
    owner_id: int
    file_url: Optional[str]
    file_hash: Optional[str]
    metadata: dict
    created_at: str


class DocumentWithLedgerResponse(BaseModel):
    """Document with ledger entries"""
    document: DocumentResponse
    ledger: List[LedgerEntryResponse]


@router.get("/document", response_model=DocumentWithLedgerResponse, summary="Get document with ledger")
def get_document(
    doc_id: int,
    session: Session = Depends(get_session)
):
    """Get document details and all associated ledger entries"""
    
    # Fetch document
    document = session.exec(
        select(Document).where(Document.id == doc_id)
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Fetch ledger entries
    ledger_entries = session.exec(
        select(LedgerEntry).where(LedgerEntry.document_id == doc_id)
        .order_by(LedgerEntry.created_at.asc())
    ).all()
    
    doc_response = DocumentResponse(
        id=document.id,
        doc_number=document.doc_number,
        doc_type=document.doc_type.value,
        owner_id=document.owner_id,
        file_url=document.file_url,
        file_hash=document.file_hash,
        metadata=document.metadata,
        created_at=document.created_at.isoformat()
    )
    
    ledger_response = [
        LedgerEntryResponse(
            id=entry.id,
            document_id=entry.document_id,
            actor_id=entry.actor_id,
            actor_role=entry.actor_role.value,
            action=entry.action.value,
            metadata=entry.metadata,
            created_at=entry.created_at.isoformat()
        )
        for entry in ledger_entries
    ]
    
    return DocumentWithLedgerResponse(
        document=doc_response,
        ledger=ledger_response
    )


@router.get("/documents", summary="List all documents")
def list_documents(
    doc_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List documents with optional filters"""
    
    query = select(Document)
    
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    
    if owner_id:
        query = query.where(Document.owner_id == owner_id)
    
    documents = session.exec(query.order_by(Document.created_at.desc())).all()
    
    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc.id,
                "doc_number": doc.doc_number,
                "doc_type": doc.doc_type.value,
                "owner_id": doc.owner_id,
                "file_hash": doc.file_hash,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]
    }


@router.get("/file", summary="Download file")
def get_file(
    file_url: str,
    session: Session = Depends(get_session)
):
    """Download file by URL"""
    import os
    from fastapi.responses import FileResponse
    
    # Security: ensure file_url doesn't contain path traversal
    if ".." in file_url or file_url.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    if not os.path.exists(file_url):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_url, media_type="application/octet-stream")

