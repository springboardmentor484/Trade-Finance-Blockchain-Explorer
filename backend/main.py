from fastapi import FastAPI
from sqlmodel import SQLModel

from backend.database import engine
from backend.routers.auth_routes import router as auth_router
from backend.routers.user import router as user_router
from backend.routers.documents import router as documents_router
from backend.routers import ledger
from backend.routers import action
from backend.routers import transactions
from backend.routers import alerts

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "Backend is running"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(documents_router)
app.include_router(ledger.router)
app.include_router(action.router)
app.include_router(transactions.router)
app.include_router(alerts.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)