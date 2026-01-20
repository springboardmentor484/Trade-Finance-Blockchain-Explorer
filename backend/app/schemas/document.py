from pydantic import BaseModel
from typing import Dict
from app.models import DocumentStatus


class DocumentCreate(BaseModel):
    doc_type: str          # ← FIXED (was DocumentType)
    doc_number: str
    file_url: str
    hash: str


class DocumentAction(BaseModel):
    action: DocumentStatus
    meta: Dict = {}


class DocumentResponse(BaseModel):
    id: int
    doc_type: str
    doc_number: str
    status: DocumentStatus
    owner_id: int
