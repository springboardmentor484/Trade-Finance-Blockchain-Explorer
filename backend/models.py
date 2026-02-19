from typing import Optional
from sqlmodel import SQLModel, Field,Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password: str
    role: str
    org: str
    # Relationships
    risk_scores: list["RiskScore"] = Relationship(back_populates="user")
    audit_logs: list["AuditLog"] = Relationship(back_populates="admin")
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    doc_number: str
    doc_type: str
    file_url: str
    transaction_id: Optional[int] = Field(default=None, foreign_key="tradetransaction.id")
    hash: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    actor_id: int = Field(foreign_key="user.id")
    action: str
    extra_metadata: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"
    expired="expired"


class TradeTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")

    amount: float
    currency: str = Field(max_length=3)

    status: TransactionStatus = Field(default=TransactionStatus.pending)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)

class TransactionAudit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transaction_id: int
    old_status: TransactionStatus
    new_status: TransactionStatus
    changed_by: int
    changed_at: datetime = Field(default_factory=datetime.utcnow)


from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int
    message: str
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, String, TIMESTAMP, func
from sqlalchemy.orm import relationship


class RiskScore(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    score: float
    rationale: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="risk_scores")


class AuditLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    admin_id: Optional[int] = Field(foreign_key="user.id")
    action: str
    target_type: str
    target_id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    admin: Optional[User] = Relationship(back_populates="audit_logs")