from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.routers import auth
from app.db.session import engine
from app.models.userModel import User
app = FastAPI(title="Trade finance backend")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    
app.include_router(auth.router)


