from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlmodel import Session, select
from passlib.context import CryptContext

from app.models import User
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.db import get_session

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
def login(email: str, password: str, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # set True in production
        samesite="lax"
    )

    return {"access_token": access_token}


@router.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_token(refresh_token)
    user_id = payload.get("sub")

    new_access_token = create_access_token({"sub": user_id})
    return {"access_token": new_access_token}
