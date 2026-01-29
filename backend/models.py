from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

# --------------------
# USER TABLE
# --------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    email: str = Field(unique=True, index=True)
    password: str
    role: str  # buyer, seller, bank, auditor

# --------------------
# DOCUMENT TABLE
# --------------------
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    doc_type: str            # PO, BOL, LOC, INVOICE
    doc_number: str

    owner_id: int = Field(foreign_key="user.id")

    file_url: str
    file_hash: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

# --------------------
# LEDGER / TIMELINE TABLE
# --------------------
class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    document_id: int = Field(foreign_key="document.id")
    actor_id: int = Field(foreign_key="user.id")

    action: str              # ISSUED, SHIPPED, RECEIVED, VERIFIED, PAID
    details: str             # JSON string (renamed from 'metadata')

    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --------------------
# PURCHASE ORDER (BUSINESS DATA)
# --------------------
class PurchaseOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")

    description: str
    amount: float

    status: str = "CREATED"
    created_at: datetime = Field(default_factory=datetime.utcnow)