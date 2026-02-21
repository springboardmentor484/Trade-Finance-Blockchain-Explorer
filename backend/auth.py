from fastapi import HTTPException
from sqlmodel import Session, select
from backend.models import User
from backend.utils import verify_password

def authenticate_user(session: Session, email: str, password: str):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return user