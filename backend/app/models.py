from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, JSON


# --------------------
# ENUMS
# --------------------

class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BANK = "bank"
    AUDITOR = "auditor"
    ADMIN = "admin"


class DocumentType(str, Enum):
    PO = "PO"
    BOL = "BOL"
    INVOICE = "INVOICE"
    LC = "LC"


class DocumentStatus(str, Enum):
    ISSUED = "ISSUED"
    ACCEPTED = "ACCEPTED"
    SHIPPED = "SHIPPED"
    RECEIVED = "RECEIVED"
    VERIFIED = "VERIFIED"
    PAID = "PAID"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"              # PO created, awaiting bank review
    IN_PROGRESS = "IN_PROGRESS"      # Bank issued LOC, auditor verified
    COMPLETED = "COMPLETED"          # All docs processed, invoice paid
    DISPUTED = "DISPUTED"            # Transaction disputed
    CANCELLED = "CANCELLED"          # Transaction cancelled


# --------------------
# USER
# --------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)
    password: str

    role: UserRole
    org_name: str   # ✅ ADDED FIELD
    
    # ✅ Transaction history for risk scoring
    completed_transactions: int = Field(default=0)
    disputed_transactions: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    documents: List["Document"] = Relationship(back_populates="owner")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="actor")


# --------------------
# DOCUMENT
# --------------------

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    doc_type: DocumentType
    doc_number: str = Field(index=True)

    owner_id: int = Field(foreign_key="user.id")

    file_url: str
    hash: str

    status: DocumentStatus = Field(default=DocumentStatus.ISSUED)

    # Required for sorting / timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="documents")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="document")


# --------------------
# LEDGER ENTRY (BLOCKCHAIN)
# --------------------

class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    document_id: int = Field(foreign_key="document.id")
    actor_id: int = Field(foreign_key="user.id")

    action: str
    meta: Dict = Field(sa_column=Column(JSON))

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    document: Optional[Document] = Relationship(back_populates="ledger_entries")
    actor: Optional[User] = Relationship(back_populates="ledger_entries")


# --------------------
# TRADE TRANSACTION
# --------------------

class TradeTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Transaction parties
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")

    # Transaction details
    amount: float
    currency: str = Field(default="USD")
    description: str

    # Trade financing
    lc_number: Optional[str] = None  # Letter of Credit number
    lc_issuer_id: Optional[int] = Field(default=None, foreign_key="user.id")  # Bank

    # Risk scoring
    risk_score: float = Field(default=0.0)  # 0-100, higher = more risk
    risk_factors: Dict = Field(sa_column=Column(JSON), default={})

    # Status
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)

    # Timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (simplified - no reverse relationships from User to avoid ambiguity)
    # buyer: Optional[User] = Relationship()
    # seller: Optional[User] = Relationship()
    # lc_issuer: Optional[User] = Relationship()
