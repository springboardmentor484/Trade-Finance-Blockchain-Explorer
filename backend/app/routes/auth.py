from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlmodel import Session, select

from app.db import get_session
from app.models import User
from app.utils.security import verify_password
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(
    email: str,
    password: str,
    response: Response,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {"sub": user.email, "role": user.role}
    )

    refresh_token = create_refresh_token({"sub": user.email})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
    )

    return {"access_token": access_token}


@router.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token")

    new_access_token = create_access_token(
        {"sub": payload["sub"]}
    )

    return {"access_token": new_access_token}
