from datetime import datetime, timedelta
from typing import Dict

from jose import jwt, JWTError

SECRET_KEY = "super-secret-key-change-this"  # move to env later
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _normalize_token(token: str) -> str:
    token = token.strip()

    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]

    return token.strip('"').strip("'")


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()

    to_encode.update({
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "access",
        "sub": str(data.get("user_id")),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()

    to_encode.update({
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "refresh",
        "sub": str(data.get("user_id")),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict:
    try:
        token = _normalize_token(token)
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
