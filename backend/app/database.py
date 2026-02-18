from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Use SQLite for development if PostgreSQL URL not set
if not DATABASE_URL or DATABASE_URL == "postgresql://localhost/trade_finance_db":
    # Development: use SQLite (file-based, no server required)
    DATABASE_URL = "sqlite:///trade_finance.db"
    DB_ENGINE_ARGS = {"check_same_thread": False}
    print("ℹ️ Using SQLite for development (sqlite:///trade_finance.db)")
else:
    # Production: use PostgreSQL
    DB_ENGINE_ARGS = {}
    print(f"ℹ️ Using PostgreSQL: {DATABASE_URL[:40]}...")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
    connect_args=DB_ENGINE_ARGS if "sqlite" in DATABASE_URL else {}
)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

def create_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)
