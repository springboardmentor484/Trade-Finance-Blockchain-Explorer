from pydantic import BaseModel
from typing import Optional, Dict

from app.models import DocumentType, DocumentStatus


# -------------------------
# CREATE DOCUMENT
# -------------------------
class DocumentCreate(BaseModel):
    doc_type: DocumentType
    doc_number: str
    file_url: str
    hash: str


# -------------------------
# DOCUMENT ACTION
# -------------------------
class DocumentAction(BaseModel):
    action: DocumentStatus
    meta: Optional[Dict] = None


# -------------------------
# DOCUMENT RESPONSE (OPTIONAL, FUTURE USE)
# -------------------------
class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    doc_number: str
    status: DocumentStatus
    owner_id: int
