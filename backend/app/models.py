from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, JSON, Enum as SQLEnum
import enum


class RoleEnum(str, enum.Enum):
    """User roles"""
    BANK = "bank"
    CORPORATE = "corporate"
    AUDITOR = "auditor"
    ADMIN = "admin"


class DocumentTypeEnum(str, enum.Enum):
    """Document types in trade finance"""
    LOC = "LOC"
    INVOICE = "INVOICE"
    BILL_OF_LADING = "BILL_OF_LADING"
    PO = "PO"
    COO = "COO"
    INSURANCE_CERT = "INSURANCE_CERT"


class LedgerActionEnum(str, enum.Enum):
    """Actions that can be recorded on ledger"""
    ISSUED = "ISSUED"
    AMENDED = "AMENDED"
    SHIPPED = "SHIPPED"
    RECEIVED = "RECEIVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    VERIFIED = "VERIFIED"


class TransactionStatusEnum(str, enum.Enum):
    """Trade transaction statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class User(SQLModel, table=True):
    """User model for authentication and organization management"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    role: RoleEnum = Field(sa_column=Column(SQLEnum(RoleEnum)))
    org_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    org_name: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Organization(SQLModel, table=True):
    """Organization model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    type: str  # bank, corporate, auditor
    country: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    """Document model for storing document metadata"""
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_number: str = Field(unique=True, index=True)
    doc_type: DocumentTypeEnum = Field(sa_column=Column(SQLEnum(DocumentTypeEnum)))
    owner_id: int = Field(foreign_key="user.id", index=True)
    file_url: Optional[str] = None
    file_hash: Optional[str] = None  # SHA-256 hash
    hash_algorithm: str = Field(default="SHA256")
    related_doc_id: Optional[int] = Field(default=None, foreign_key="document.id")
    additional_metadata: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerEntry(SQLModel, table=True):
    """Ledger entry for tracking document lifecycle"""
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id", index=True)
    actor_id: int = Field(foreign_key="user.id")
    actor_role: RoleEnum = Field(sa_column=Column(SQLEnum(RoleEnum)))
    action: LedgerActionEnum = Field(sa_column=Column(SQLEnum(LedgerActionEnum)))
    additional_metadata: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TradeTransaction(SQLModel, table=True):
    """Trade transaction model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(unique=True, index=True)
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")
    amount: float
    currency: str = Field(default="USD")
    status: TransactionStatusEnum = Field(
        default=TransactionStatusEnum.PENDING,
        sa_column=Column(SQLEnum(TransactionStatusEnum))
    )
    po_doc_id: Optional[int] = Field(default=None, foreign_key="document.id")
    loc_doc_id: Optional[int] = Field(default=None, foreign_key="document.id")
    bol_doc_id: Optional[int] = Field(default=None, foreign_key="document.id")
    invoice_doc_id: Optional[int] = Field(default=None, foreign_key="document.id")
    additional_metadata: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class RiskScore(SQLModel, table=True):
    """Risk scoring for users"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, unique=True)
    completed_count: int = Field(default=0)
    total_count: int = Field(default=0)
    disputed_count: int = Field(default=0)
    risk_score: float = Field(default=0.0)  # percentage
    rationale: str = Field(default="")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Audit log for tracking all actions"""
    id: Optional[int] = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="user.id")
    action: str
    target_type: str  # user, document, transaction, etc.
    target_id: int
    changes: dict = Field(default={}, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RefreshToken(SQLModel, table=True):
    """Store refresh tokens for validating token refresh requests"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token_hash: str = Field(unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_revoked: bool = Field(default=False)

