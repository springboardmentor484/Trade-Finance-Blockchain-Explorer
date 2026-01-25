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


# --------------------
# USER
# --------------------

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password: str
    role: UserRole
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

    # 🔥 REQUIRED for Step 2.1 sorting
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
