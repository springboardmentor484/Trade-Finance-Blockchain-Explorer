from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, JSON, UniqueConstraint


# =====================================================
# ENUMS
# =====================================================

class UserRole(str, Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    BANK = "BANK"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"


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
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"


# =====================================================
# USER
# =====================================================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True, unique=True)
    password: str

    role: UserRole
    org_name: str

    # Risk Metrics
    completed_transactions: int = Field(default=0)
    disputed_transactions: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    documents: List["Document"] = Relationship(back_populates="owner")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="actor")


# =====================================================
# TRADE TRANSACTION (CORE ENGINE)
# =====================================================

class TradeTransaction(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("lc_number", name="uq_lc_number"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # Parties
    buyer_id: int = Field(foreign_key="user.id", index=True)
    seller_id: int = Field(foreign_key="user.id", index=True)

    # Financials
    amount: float
    currency: str = Field(default="USD")
    description: str

    # Letter of Credit
    lc_number: Optional[str] = Field(default=None, index=True)
    lc_issuer_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Status
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)

    # Timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    documents: List["Document"] = Relationship(back_populates="transaction")
    risk_scores: List["RiskScore"] = Relationship(back_populates="transaction")


# =====================================================
# DOCUMENT (STRICT WORKFLOW LINK)
# =====================================================

class Document(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("doc_number", "transaction_id", name="uq_doc_per_transaction"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    doc_type: DocumentType
    doc_number: str = Field(index=True)

    # Owner
    owner_id: int = Field(foreign_key="user.id", index=True)

    # STRICT transaction link
    transaction_id: int = Field(foreign_key="tradetransaction.id", index=True)

    # Storage abstraction (S3-ready)
    file_url: str
    file_storage_provider: str = Field(default="LOCAL")  # LOCAL | S3
    hash: str

    status: DocumentStatus = Field(default=DocumentStatus.ISSUED)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="documents")
    ledger_entries: List["LedgerEntry"] = Relationship(back_populates="document")
    transaction: Optional[TradeTransaction] = Relationship(back_populates="documents")


# =====================================================
# LEDGER ENTRY (IMMUTABLE AUDIT CHAIN)
# =====================================================

class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    document_id: int = Field(foreign_key="document.id", index=True)
    actor_id: int = Field(foreign_key="user.id", index=True)

    action: str
    meta: Dict = Field(sa_column=Column(JSON))

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    document: Optional[Document] = Relationship(back_populates="ledger_entries")
    actor: Optional[User] = Relationship(back_populates="ledger_entries")


# =====================================================
# RISK SCORE (ONE ACTIVE SCORE PER TRANSACTION)
# =====================================================

class RiskScore(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_risk_per_transaction"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    transaction_id: int = Field(foreign_key="tradetransaction.id", index=True)

    score: float
    factors: Dict = Field(sa_column=Column(JSON))

    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    transaction: Optional[TradeTransaction] = Relationship(back_populates="risk_scores")
