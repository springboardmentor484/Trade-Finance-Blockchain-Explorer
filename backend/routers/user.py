from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models import User
from schemas import UserCreate, UserRead
from utils import hash_password

router = APIRouter()

@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user