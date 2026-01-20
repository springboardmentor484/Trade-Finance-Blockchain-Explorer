from fastapi import APIRouter, Response

from app.utils.jwt import create_access_token, create_refresh_token
from app.models import UserRole

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(response: Response):
    """
    TEMP LOGIN (Week 5)
    Later: validate username/password from DB
    """

    # Hardcoded user (for now)
    user_id = 1
    role = UserRole.BUYER

    access_token = create_access_token(
        {"user_id": user_id, "role": role.value}
    )
    refresh_token = create_refresh_token(
        {"user_id": user_id, "role": role.value}
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
