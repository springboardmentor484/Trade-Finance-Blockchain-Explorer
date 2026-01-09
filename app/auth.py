import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
