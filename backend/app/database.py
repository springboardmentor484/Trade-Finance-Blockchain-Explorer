import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv( "DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"sslmode": "require"},
)


def get_session():
    with Session(engine) as session:
        yield session

