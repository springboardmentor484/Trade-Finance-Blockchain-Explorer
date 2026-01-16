import jwt
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from sqlmodel import SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, get_session
from app.models import User
from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    get_current_user,
    require_role,
)

from jwt import ExpiredSignatureError, InvalidTokenError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SQLModel.metadata.create_all(engine)

# ---------------- WEEK 1 ----------------

@app.post("/create-user")
def create_user(
    name: str,
    email: str,
    password: str,
    role: str,
    org_name: str,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        role=role,
        org_name=org_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "User created"}


@app.post("/login")
def login(
    email: str,
    password: str,
    response: Response,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role,
            "org": user.org_name,
        }
    )

    refresh_token = create_refresh_token({"user_id": user.id})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
    )

    return {"access_token": access_token}


@app.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(
        {
            "user_id": payload["user_id"],
        }
    )

    return {"access_token": new_access_token}


# ---------------- WEEK 2 ----------------

@app.get("/protected")
def protected(user: dict = Depends(get_current_user)):
    return {
        "message": "Protected route accessed",
        "user": user,
    }


@app.get("/admin-only")
def admin_only(user=Depends(require_role("admin"))):
    return {"message": "Admin access granted"}


@app.get("/user")
def get_user_profile(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = session.get(User, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "org": user.org_name,
        "role": user.role,
    }
