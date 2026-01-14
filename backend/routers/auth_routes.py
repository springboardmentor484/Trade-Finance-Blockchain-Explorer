from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import select
from backend.database import get_session
from backend.models import User
from backend.utils import verify_password, create_access_token, create_refresh_token
from fastapi.responses import JSONResponse
from sqlmodel import Session

router = APIRouter(prefix="/auth")

# Signup
@router.post("/signup")
def signup(user: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user.password = create_access_token({"password": user.password})  # simple hash
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully"}

# Login
@router.post("/login")
def login(credentials: dict, response: Response, session: Session = Depends(get_session)):
    email = credentials.get("email")
    password = credentials.get("password")

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
@router.post("/refresh")
def refresh(response: Response, refresh_token: str = Depends(lambda: None)):
    from jose import jwt, JWTError
    from fastapi import Cookie

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

  