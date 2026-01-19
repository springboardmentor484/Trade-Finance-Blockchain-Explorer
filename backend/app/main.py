from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app import models

app = FastAPI(title="Trade Finance Blockchain Explorer")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"status": "Backend running"}
