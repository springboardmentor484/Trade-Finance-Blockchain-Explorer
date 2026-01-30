from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT config
SECRET_KEY = "CHANGE_THIS_SECRET_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # refresh token lasts 7 days
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from backend.models import User
from backend.database import get_session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from backend.utils import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")