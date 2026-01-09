import jwt
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from sqlmodel import SQLModel, select, Session
from app.database import engine, get_session
from app.models import User
from app.auth import create_access_token, create_refresh_token, hash_password, verify_password
from jwt import ExpiredSignatureError, InvalidTokenError

app = FastAPI()


SQLModel.metadata.create_all(engine)


@app.post("/create-user")
def create_user(name: str, email: str, password: str, role: str, org_name: str, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(password)
    user = User(name=name, email=email, password=hashed_pw, role=role, org_name=org_name)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"msg": "User created successfully", "user": {"id": user.id, "name": user.name, "email": user.email}}


@app.post("/login")
def login(email: str, password: str, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return {"access_token": access_token}


@app.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = jwt.decode(refresh_token, "SECRET123", algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access_token = create_access_token({"user_id": payload["user_id"]})
    return {"access_token": new_access_token}

