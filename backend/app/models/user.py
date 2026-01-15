from sqlmodel import Field, SQLModel, create_engine

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str
    id_password: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)