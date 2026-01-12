from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any, Optional
from jose import jwt
from app.core.config import ALGORITHM,  ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY,JWT_REFRESH_SECRET_KEY

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(data: dict, expire_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expire_delta if expire_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode = {"exp": expire, "sub": data}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expire_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expire_delta if expire_delta else timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode = {"exp": expire, "sub": data}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
