from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.utils.jwt import create_access_token, create_refresh_token
from app.models import UserRole

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------- SCHEMAS ----------
class LoginRequest(BaseModel):
    user_id: int
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- ROUTES ----------
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """
    TEMP LOGIN (no DB yet)
    """
    payload = {
        "user_id": data.user_id,
        "role": data.role.value,
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
