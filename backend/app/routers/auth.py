from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.user import SignupRequest, LoginRequest
from app.services.auth_service import create_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])
    
@router.post("/signup", summary="Create new user")
async def signup(data: SignupRequest, session: Session = Depends(get_session)):
    return create_user(data, session)

@router.post("/login")
def login(
    data: LoginRequest,
    session: Session = Depends(get_session)):
    return login_user(data, session)
    
    