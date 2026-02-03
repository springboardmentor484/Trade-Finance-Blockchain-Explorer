from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlmodel import select
from backend.database import get_session
from backend.models import User
from backend.schemas import SignupRequest, LoginRequest, TokenResponse
from backend.utils import hash_password, verify_password, create_access_token, create_refresh_token
from jose import JWTError, jwt
from fastapi import Cookie

router = APIRouter(prefix="/auth", tags=["Auth"])

# Signup
@router.post("/signup")
def signup(data: SignupRequest, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        org=data.org,
        role=data.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully"}

# Login
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, session: Session = Depends(get_session)):
    email = data.email
    password = data.password

    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict"
    )

    return {"access_token": access_token, "token_type": "bearer"}

# Refresh token
@router.post("/refresh", response_model=TokenResponse)
def refresh(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    try:
        payload = jwt.decode(refresh_token, "CHANGE_THIS_SECRET_LATER", algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        new_access_token = create_access_token({"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

from fastapi import Depends
from backend.utils import get_current_user  # we will create this function

@router.get("/user")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "org": current_user.org,
        "role": current_user.role
    }


    