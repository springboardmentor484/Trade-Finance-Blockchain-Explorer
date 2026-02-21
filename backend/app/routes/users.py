from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from ..db import get_session, engine
from ..models import User
from ..schemas.user import UserCreate, UserResponse
from ..utils.security import hash_password
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate):
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            role=data.role,
            org_name=data.org_name,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


@router.get("", response_model=UserResponse)
def get_current_user_profile(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user = session.get(User, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
