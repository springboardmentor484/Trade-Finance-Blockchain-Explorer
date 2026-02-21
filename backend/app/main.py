from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .db import engine
from . import models  # Ensure models are imported before create_all

# Routers
from .routes.auth import router as auth_router
from .routes.users import router as user_router
from .routes.documents import router as document_router
from .routes.transactions import router as transaction_router
from .routes.analytics import router as analytics_router
from .routes.exports import router as export_router

# Services
from .services.integrity_scheduler import start_integrity_scheduler


# ---------------------------------------------------
# Create FastAPI App
# ---------------------------------------------------

app = FastAPI(title="Trade Finance Blockchain Explorer")


# ---------------------------------------------------
# CORS Middleware (must be before routers)
# ---------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Include Routers
# ---------------------------------------------------

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(document_router)
app.include_router(transaction_router)
app.include_router(analytics_router)
app.include_router(export_router)


# ---------------------------------------------------
# Startup Event
# ---------------------------------------------------

@app.on_event("startup")
def on_startup():
    # Create DB tables
    SQLModel.metadata.create_all(engine)

    # Start background integrity scheduler
    start_integrity_scheduler()


# ---------------------------------------------------
# Root Endpoint
# ---------------------------------------------------

@app.get("/")
def root():
    return {"status": "Backend running"}
