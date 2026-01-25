from datetime import datetime, timedelta
from typing import Dict

from jose import jwt, JWTError

# 🔐 JWT CONFIG
SECRET_KEY = "super-secret-key-change-this"  # move to env later
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _normalize_token(token: str) -> str:
    """
    Normalize JWT coming from Authorization header.
    Handles:
    - Bearer <token>
    - Quoted tokens (Swagger issue)
    - Extra whitespace
    """
    token = token.strip()

    # Remove Bearer prefix if present
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]

    # 🔥 CRITICAL FIX: remove surrounding quotes
    token = token.strip('"').strip("'")

    return token


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()

    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
        "sub": str(data.get("user_id")),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict) -> str:
    to_encode = data.copy()

    now = datetime.utcnow()
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
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
        # Never leak jose internals
        raise ValueError("Invalid or expired token")
