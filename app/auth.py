import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Load .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def create_access_token(data: dict, minutes: int = 15):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, days: int = 7):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(days=days)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)




def hash_password(password: str):
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return role_checker
