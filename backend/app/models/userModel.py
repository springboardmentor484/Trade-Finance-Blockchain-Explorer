from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    org: str
    role: str
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    