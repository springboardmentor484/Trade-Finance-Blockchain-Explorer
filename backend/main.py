from fastapi import FastAPI
from sqlmodel import SQLModel

from backend.database import engine
from backend import models  # IMPORTANT: registers all models
from backend.routers.auth_routes import router

app = FastAPI(title="Trade Finance Blockchain Explorer")
app.include_router(router)


# Create database tables on startup
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "Trade Finance API is running"}