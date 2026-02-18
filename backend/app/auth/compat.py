from fastapi import APIRouter, HTTPException, Depends, Response, Request
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta

from app.database import get_session
from app.models import User, RefreshToken, RoleEnum
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login_root(payload: LoginRequest, response: Response, session: Session = Depends(get_session)):
    # Duplicate of /api/auth/login to provide compatibility with APIContract
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    access_token = create_access_token(user_id=user.id, email=user.email, role=user.role.value)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)

    token_hash = hash_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
    session.add(rt)
    session.commit()

    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7*24*60*60
    )

    return {"accessToken": access_token}


@router.post("/refresh")
def refresh_root(request: Request, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    token_data = verify_token(refresh_token)
    if not token_data or token_data.token_type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    token_hash = hash_token(refresh_token)
    rt = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.is_revoked == False)).first()
    if not rt or rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access = create_access_token(user_id=user.id, email=user.email, role=user.role.value)
    return {"accessToken": new_access}


@router.get("/user")
def user_root(authorization: str = None, session: Session = Depends(get_session)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token_data = verify_token(token)
    if not token_data or token_data.token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = session.exec(select(User).where(User.id == token_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": user.name, "email": user.email, "org": user.org_name, "role": user.role.value}
