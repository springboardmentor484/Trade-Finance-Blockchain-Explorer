from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.database import get_session
from backend.models import User
from backend.utils import get_current_user
from backend.schemas import UserRead

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile", response_model=UserRead)
def profile(current_user: User = Depends(get_current_user)):
    return {
        "name":current_user.name,
        "email":current_user.email,
        "org":current_user.org,
        "role":current_user.role
    }