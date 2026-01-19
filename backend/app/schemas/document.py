from pydantic import BaseModel
from typing import Optional, Dict
from app.models import DocumentType, DocumentStatus


class DocumentCreate(BaseModel):
    doc_type: DocumentType
    doc_number: str
    file_url: str
    hash: str


class DocumentAction(BaseModel):
    action: str
    meta: Dict


class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    doc_number: str
    status: DocumentStatus
    owner_id: int
