from fastapi import FastAPI
from sqlmodel import SQLModel
from backend.database import engine
from backend.auth.routes import router as auth_router

app = FastAPI()

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router, prefix="/auth")
