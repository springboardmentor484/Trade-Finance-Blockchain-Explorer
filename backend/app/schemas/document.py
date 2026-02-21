from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from ..models import DocumentType, DocumentStatus


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
# (🔥 AUDIT TRAIL ENHANCED)
# -------------------------
class DocumentAction(BaseModel):
    action: DocumentStatus
    meta: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None  # 👈 WHY this action was taken


# -------------------------
# BASIC DOCUMENT RESPONSE
# -------------------------
class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    doc_number: str
    status: DocumentStatus
    owner_id: int

    model_config = {"from_attributes": True}


# =========================================================
# 🔥 MILESTONE 2 — STEP 2.3 (PRODUCTION SCHEMAS)
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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


# -------------------------
# DOCUMENT READ RESPONSE
# (Used by /documents/{id}/read)
# -------------------------
class DocumentReadResponse(BaseModel):
    document: DocumentResponse
    ledger: List[LedgerEntryResponse]
    allowed_actions: List[DocumentStatus]

    model_config = {"from_attributes": True}


# -------------------------
# ALLOWED ACTIONS RESPONSE
# (Used by /documents/{id}/allowed-actions)
# -------------------------
class AllowedActionsResponse(BaseModel):
    current_status: DocumentStatus
    allowed_actions: List[DocumentStatus]

    model_config = {"from_attributes": True}
