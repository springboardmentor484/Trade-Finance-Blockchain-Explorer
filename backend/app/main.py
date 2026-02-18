from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.auth.compat import router as auth_compat_router
from app.routes.documents import router as documents_router
from app.routes.document import router as document_router
from app.routes.upload import router as upload_router
from app.routes.action import router as action_router
from app.routes.risk import router as risk_router
from app.routes.transactions import router as transactions_router
from app.routes.trades import router as trades_router
from app.database import create_tables

tags_metadata = [
    {"name": "auth", "description": "Authentication & user management"},
    {"name": "documents", "description": "Upload, view and act on documents"},
    {"name": "actions", "description": "Trade flow actions and permissions"},
    {"name": "risk", "description": "Risk scoring and analytics"},
    {"name": "transactions", "description": "Trade transaction management"},
    {"name": "trades", "description": "Trade flow orchestration"},
    {"name": "default", "description": "Health and root endpoints"}
]

app = FastAPI(
    title="Trade Finance Blockchain Explorer",
    version="1.0.0",
    description="Multi-role trade finance platform with blockchain audit trail, risk scoring, and analytics",
    openapi_tags=tags_metadata,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/", tags=["default"], summary="Root")
def root():
    return {
        "message": "Trade Finance Blockchain Explorer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "documents": "/api/documents",
            "actions": "/api/actions",
            "risk": "/api/risk",
            "transactions": "/api/transactions",
            "trades": "/api/trades"
        }
    }

@app.get("/health", tags=["default"], summary="Health check")
def health():
    return {"status": "ok", "service": "Trade Finance API"}

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(action_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(trades_router, prefix="/api")
app.include_router(auth_compat_router)

