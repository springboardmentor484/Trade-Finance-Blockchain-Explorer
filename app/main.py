from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import auth, users

app = FastAPI(title="Trade Finance Blockchain Explorer")

SQLModel.metadata.create_all(engine)

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")

@app.get("/")
def root():
    return {"message": "Landing page"}
