from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


# ---------------- ENUMS ----------------

class UserRole(str, Enum):
    bank = "bank"
    corporate = "corporate"
    auditor = "auditor"
    admin = "admin"


class DocumentType(str, Enum):
    LOC = "LOC"
    INVOICE = "INVOICE"
    BILL_OF_LADING = "BILL_OF_LADING"
    PO = "PO"
    COO = "COO"
    INSURANCE_CERT = "INSURANCE_CERT"


class LedgerAction(str, Enum):
    ISSUED = "ISSUED"
    AMENDED = "AMENDED"
    SHIPPED = "SHIPPED"
    RECEIVED = "RECEIVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    VERIFIED = "VERIFIED"


class TradeStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"


# ---------------- TABLES ----------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password: str
    role: UserRole
    org_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    doc_type: DocumentType
    doc_number: str
    file_url: str
    hash: str
    issued_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    action: LedgerAction
    actor_id: int = Field(foreign_key="user.id")
    event_metadata: dict = Field(sa_column=Column("metadata", JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TradeTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")
    amount: float
    currency: str
    status: TradeStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RiskScore(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    score: float
    rationale: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="user.id")
    action: str
    target_type: str
    target_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
