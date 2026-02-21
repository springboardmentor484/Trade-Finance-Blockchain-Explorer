from sqlmodel import Session
from app.db import engine
from app.models import User, UserRole
from app.utils.security import hash_password

try:
    with Session(engine) as session:
        user = User(
            name="Test",
            email="test2@example.com",
            password=hash_password("password123"),
            role=UserRole.BUYER,
            org_name="TestCorp"
        )
        session.add(user)
        session.commit()
        print("User created successfully!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
