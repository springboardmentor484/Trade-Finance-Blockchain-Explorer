from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def can_perform_action(user_role: str, doc_type: str, action: str) -> bool:
    """
    Checks if a user role is allowed to perform an action on a document type
    """

    rules = {
        ("buyer", "BOL", "RECEIVED"),
        ("seller", "BOL", "SHIPPED"),
        ("seller", "PO", "ISSUE_BOL"),
        ("seller", "BOL", "ISSUE_INVOICE"),
        ("auditor", "PO", "VERIFY"),
        ("auditor", "LOC", "VERIFY"),
        ("bank", "INVOICE", "PAID"),
        ("bank", "LOC", "ISSUE_LOC"),
    }

    return (user_role, doc_type, action) in rules