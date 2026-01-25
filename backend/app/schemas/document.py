from pydantic import BaseModel
from typing import Optional, Dict, List, Any

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
    meta: Optional[Dict[str, Any]] = None


# -------------------------
# BASIC DOCUMENT RESPONSE
# -------------------------
class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    doc_number: str
    status: DocumentStatus
    owner_id: int

    class Config:
        orm_mode = True


# =========================================================
# 🔥 MILESTONE 2 — STEP 2.3 (NEW SCHEMAS)
# =========================================================

# -------------------------
# LEDGER ENTRY RESPONSE
# -------------------------
class LedgerEntryResponse(BaseModel):
    id: int
    document_id: int
    actor_id: int
    action: str
    meta: Dict[str, Any]

    class Config:
        orm_mode = True


# -------------------------
# DOCUMENT DETAIL RESPONSE
# (Single-call production API)
# -------------------------
class DocumentDetailResponse(BaseModel):
    id: int
    doc_type: DocumentType
    doc_number: str
    status: DocumentStatus
    owner_id: int

    ledger: List[LedgerEntryResponse]
    allowed_actions: List[DocumentStatus]

    class Config:
        orm_mode = True
