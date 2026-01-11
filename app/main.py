from fastapi import FastAPI
from sqlmodel import SQLModel

from app.db import engine
from app.routes.auth import router as auth_router

app = FastAPI(title="Trade Finance Blockchain Explorer")

app.include_router(auth_router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
@app.get("/")
def root():
    return {"message": "Dashboard is running! Go to /docs to login and see transactions."}
