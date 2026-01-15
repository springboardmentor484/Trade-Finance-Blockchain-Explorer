from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.userModel import User
from app.schemas.user import SignupRequest, LoginRequest
from app.core.security import get_hashed_password, verify_password, create_access_token,create_refresh_token

def create_user(data: SignupRequest, session: Session):
    user = User(
    name=data.name,
    email=data.email,
    password_hash=get_hashed_password(data.password),
    org=data.org,
    role=data.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def login_user(data: LoginRequest, session: Session):
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credntials")
    
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email)
    }