from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class TransactionCreate(BaseModel):
    """Request body for creating a transaction"""
    buyer_id: int
    seller_id: int
    amount: float
    currency: str = "USD"
    description: str
    lc_number: Optional[str] = None
    lc_issuer_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    """Request body for updating transaction status"""
    status: str  # PENDING, IN_PROGRESS, COMPLETED, DISPUTED, CANCELLED
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    """Response for transaction"""
    id: int
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    description: str
    lc_number: Optional[str]
    lc_issuer_id: Optional[int]
    risk_score: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionDetailResponse(BaseModel):
    """Detailed transaction response with risk factors"""
    id: int
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    description: str
    lc_number: Optional[str]
    lc_issuer_id: Optional[int]
    risk_score: float
    risk_factors: Dict
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
