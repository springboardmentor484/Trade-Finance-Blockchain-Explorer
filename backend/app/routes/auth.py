from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import Session, select

from ..db import engine
from ..models import User
from ..schemas.user import UserLogin
from ..utils.jwt import create_access_token, create_refresh_token
from ..utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: UserLogin, response: Response):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if not user or not verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        payload = {
            "user_id": user.id,
            "role": user.role.value,
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
