from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlmodel import Session, select
from passlib.context import CryptContext
from pydantic import BaseModel

from backend.database import get_session
from backend.models import User
from backend.auth.jwt import create_access_token, create_refresh_token, decode_token

router = APIRouter()
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)



class LoginRequest(BaseModel):
    email: str
    password: str

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

@router.post("/login")
def login(data: LoginRequest, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax"
    )

    return {"access_token": access_token}

@router.post("/refresh")
def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(token)
    return {"access_token": create_access_token({"sub": payload["sub"]})}
