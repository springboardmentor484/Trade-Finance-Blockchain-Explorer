from fastapi import FastAPI
from sqlmodel import SQLModel

from backend.database import engine
from backend.routers.auth_routes import router as auth_router
from backend.routers.user import router as user_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "Backend is running"}


app.include_router(auth_router)
app.include_router(user_router)