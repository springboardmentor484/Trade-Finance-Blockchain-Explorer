from datetime import datetime, timedelta
from typing import Dict

from jose import jwt, JWTError

SECRET_KEY = "super-secret-key-change-this"  # TODO: move to env
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# =====================================================
# INTERNAL TOKEN NORMALIZER
# =====================================================

def _normalize_token(token: str) -> str:
    token = token.strip()

    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]

    return token.strip('"').strip("'")


# =====================================================
# CREATE ACCESS TOKEN
# =====================================================

def create_access_token(data: Dict) -> str:
    now = datetime.utcnow()

    payload = data.copy()
    payload.update({
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "type": "access",
        "sub": str(data.get("user_id")),
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# CREATE REFRESH TOKEN
# =====================================================

def create_refresh_token(data: Dict) -> str:
    now = datetime.utcnow()

    payload = data.copy()
    payload.update({
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "refresh",
        "sub": str(data.get("user_id")),
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =====================================================
# GENERIC TOKEN DECODE
# =====================================================

def decode_token(token: str) -> Dict:
    try:
        token = _normalize_token(token)
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")


# =====================================================
# VERIFY ACCESS TOKEN
# =====================================================

def verify_access_token(token: str) -> Dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("Invalid access token type")

    if not payload.get("sub"):
        raise ValueError("Access token missing subject")

    return payload


# =====================================================
# VERIFY REFRESH TOKEN
# =====================================================

def verify_refresh_token(token: str) -> Dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token type")

    if not payload.get("sub"):
        raise ValueError("Refresh token missing subject")

    return payload


# =====================================================
# EXTRACT USER ID SAFELY
# =====================================================

def get_user_id_from_token(token: str) -> int:
    payload = decode_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token missing subject")

    return int(user_id)
