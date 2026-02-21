from fastapi import APIRouter, HTTPException, Response, Request, status
from sqlmodel import Session, select
from datetime import timedelta

from ..db import engine
from ..models import User
from ..schemas.user import UserLogin
from ..utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ..utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# =====================================================
# LOGIN
# =====================================================

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
            "type": "access",
        }

        access_token = create_access_token(payload)

        refresh_payload = {
            "user_id": user.id,
            "role": user.role.value,
            "type": "refresh",
        }

        refresh_token = create_refresh_token(refresh_payload)

        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # change to True in production (HTTPS)
            samesite="lax",
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }


# =====================================================
# REFRESH TOKEN ENDPOINT
# =====================================================

@router.post("/refresh")
def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_access_payload = {
        "user_id": payload["user_id"],
        "role": payload["role"],
        "type": "access",
    }

    new_refresh_payload = {
        "user_id": payload["user_id"],
        "role": payload["role"],
        "type": "refresh",
    }

    # Create new tokens (rotation)
    new_access_token = create_access_token(new_access_payload)
    new_refresh_token = create_refresh_token(new_refresh_payload)

    # Rotate refresh cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # change to True in production
        samesite="lax",
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# =====================================================
# LOGOUT
# =====================================================

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
