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
            # 🔥 FIX: update role to UPPERCASE if it was seeded as lowercase before
            if existing.role != 'ADMIN':
                existing.role = 'ADMIN'
                session.add(existing)
                session.commit()
                print('✅ Admin role updated to ADMIN (uppercase)')
            else:
                print('✅ Admin user already exists')
            return

        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password=hash_password('admin123'),
            role='ADMIN',  # 🔥 FIXED: uppercase to match backend role system
            org_name='Admin Org'
        )
        session.add(admin)
        session.commit()
        print('✅ Admin user created successfully')
        print('   Email: admin@example.com')
        print('   Password: admin123')

if __name__ == '__main__':
    seed_admin()