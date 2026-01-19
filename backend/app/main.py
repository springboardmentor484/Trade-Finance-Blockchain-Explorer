from fastapi import FastAPI
from app.routes.auth import router as auth_router
from sqlmodel import SQLModel

from app.db import engine
from app import models

app = FastAPI(title="Trade Finance Blockchain Explorer")
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"status": "Backend running"}
