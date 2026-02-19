from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .db import engine
from .routes.auth import router as auth_router
from .routes.users import router as user_router
from .routes.documents import router as document_router
from .routes.transactions import router as transaction_router
from .routes.analytics import router as analytics_router
from . import models

app = FastAPI(title="Trade Finance Blockchain Explorer")

# ✅ CORS MUST come FIRST before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers AFTER middleware
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(transaction_router)
app.include_router(analytics_router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"status": "Backend running"}
