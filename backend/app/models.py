from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional 
from sqlalchemy import Column, JSON

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: str
    org_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_type: str
    doc_number: str
    file_url: str
    file_hash: str

    owner_id: int
    buyer_id: int
    seller_id: int

    status: str = Field(default="CREATED")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    document_id: int
    actor_id: int
    action:str

    extra_data: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int
    seller_id: int
    currency: str
    amount: float
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)