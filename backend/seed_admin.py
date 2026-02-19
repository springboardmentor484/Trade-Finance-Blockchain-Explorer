#!/usr/bin/env python3
"""Seed the database with initial admin user"""

from app.models import User
from app.db import engine
from app.utils.security import hash_password
from sqlmodel import Session, select

def seed_admin():
    with Session(engine) as session:
        # Check if admin exists
        existing = session.exec(select(User).where(User.email == 'admin@example.com')).first()
        if existing:
            print('✅ Admin user already exists')
            return
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password=hash_password('admin123'),
            role='admin',
            org_name='Admin Org'
        )
        session.add(admin)
        session.commit()
        print('✅ Admin user created successfully')
        print('   Email: admin@example.com')
        print('   Password: admin123')

if __name__ == '__main__':
    seed_admin()
