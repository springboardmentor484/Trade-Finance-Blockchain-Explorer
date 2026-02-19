from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# -------------------------------------------------
# DATABASE PATH (ABSOLUTE & SAFE)
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "trade_finance.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

# -------------------------------------------------
# ENGINE
# -------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)

# -------------------------------------------------
# SESSION DEPENDENCY
# -------------------------------------------------

def get_session():
    with Session(engine) as session:
        yield session
