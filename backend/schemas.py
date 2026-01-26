from pydantic import BaseModel
from typing import Optional,Dict,List
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UploadDocumentSchema(BaseModel):
    doc_number: str
    seller_id: int

class ActionSchema(BaseModel):
    doc_id: int
    action: str
    metadata: Optional[Dict] = None

class LedgerResponse(BaseModel):
    actor_id: int
    action: str
    metadata: Optional[Dict]
    timestamp: datetime

class DocumentResponse(BaseModel):
    id: int
    doc_type: str
    doc_number: str
    file_url: str
    owner_id: int
    ledger: List[LedgerResponse]