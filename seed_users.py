#!/usr/bin/env python3
"""Seed demo users for testing"""

import sys
sys.path.insert(0, '.')

from backend.app.models import User
from backend.app.db import engine
from backend.app.utils.security import hash_password
from sqlmodel import Session, select

credentials = [
    {'email': 'buyer@example.com', 'password': 'buyer123', 'role': 'buyer', 'name': 'John Buyer', 'org': 'Buyer Corp'},
    {'email': 'seller@example.com', 'password': 'seller123', 'role': 'seller', 'name': 'Jane Seller', 'org': 'Seller Inc'},
]

with Session(engine) as session:
    for cred in credentials:
        existing = session.exec(select(User).where(User.email == cred['email'])).first()
        if existing:
            print(f"✅ {cred['role'].capitalize()} user already exists: {cred['email']}")
        else:
            user = User(
                name=cred['name'],
                email=cred['email'],
                password=hash_password(cred['password']),
                role=cred['role'],
                org_name=cred['org']
            )
            session.add(user)
            session.commit()
            print(f"✅ {cred['role'].capitalize()} user created: {cred['email']}")
