from sqlmodel import Session
from passlib.context import CryptContext

from backend.database import engine
from backend.models import User, UserRole

# IMPORTANT: use pbkdf2_sha256 ONLY
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def main():
    hashed_password = pwd_context.hash("password123")

    user = User(
        name="Test User",
        email="test@example.com",
        password=hashed_password,
        role=UserRole.admin,
        org_name="TestOrg"
    )

    with Session(engine) as session:
        session.add(user)
        session.commit()

    print("✅ User created successfully")

if __name__ == "__main__":
    main()
