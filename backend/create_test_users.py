#!/usr/bin/env python3
"""
Script to create test users with different roles for Joulaa platform
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.core.security import get_password_hash
from datetime import datetime
import uuid

# Test users data
TEST_USERS = [
    {
        "email": "admin@joulaa.com",
        "username": "admin",
        "password": "Admin123!",
        "full_name_ar": "مدير النظام",
        "full_name_en": "System Administrator",
        "role": "admin",
        "language_preference": "ar",
        "is_verified": True
    },
    {
        "email": "manager@joulaa.com",
        "username": "manager",
        "password": "Manager123!",
        "full_name_ar": "مدير المشروع",
        "full_name_en": "Project Manager",
        "role": "manager",
        "language_preference": "ar",
        "is_verified": True
    },
    {
        "email": "user@joulaa.com",
        "username": "user",
        "password": "User123!",
        "full_name_ar": "مستخدم عادي",
        "full_name_en": "Regular User",
        "role": "user",
        "language_preference": "ar",
        "is_verified": True
    },
    {
        "email": "viewer@joulaa.com",
        "username": "viewer",
        "password": "Viewer123!",
        "full_name_ar": "مشاهد",
        "full_name_en": "Viewer",
        "role": "viewer",
        "language_preference": "ar",
        "is_verified": True
    },
    {
        "email": "test@joulaa.com",
        "username": "testuser",
        "password": "Test123!",
        "full_name_ar": "مستخدم تجريبي",
        "full_name_en": "Test User",
        "role": "user",
        "language_preference": "en",
        "is_verified": True
    }
]

async def create_test_users():
    """Create test users in the database"""
    
    # Create async engine with correct driver
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        echo=True
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("Creating test users...")
            
            for user_data in TEST_USERS:
                # Check if user already exists using raw SQL
                existing_user = await session.execute(
                    text("SELECT id FROM users WHERE email = :email OR username = :username"),
                    {"email": user_data["email"], "username": user_data["username"]}
                )
                if existing_user.fetchone():
                    print(f"User {user_data['username']} already exists, skipping...")
                    continue
                
                # Create new user using raw SQL
                user_id = str(uuid.uuid4())
                password_hash = get_password_hash(user_data["password"])
                
                await session.execute(
                    text("""
                        INSERT INTO users (
                            id, email, username, password_hash, full_name_ar, full_name_en,
                            role, language_preference, timezone, is_active,
                            is_verified, created_at, updated_at
                        ) VALUES (
                            :id, :email, :username, :password_hash, :full_name_ar, :full_name_en,
                            :role, :language_preference, :timezone, :is_active,
                            :is_verified, :created_at, :updated_at
                        )
                    """),
                    {
                        "id": user_id,
                        "email": user_data["email"],
                        "username": user_data["username"],
                        "password_hash": password_hash,
                        "full_name_ar": user_data["full_name_ar"],
                        "full_name_en": user_data["full_name_en"],
                        "role": user_data["role"],
                        "language_preference": user_data["language_preference"],
                        "timezone": "Asia/Riyadh",
                        "is_active": True,
                        "is_verified": user_data["is_verified"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                
                print(f"Created user: {user_data['username']} ({user_data['role']})")
            
            await session.commit()
            print("\n✅ All test users created successfully!")
            
            # Print summary
            print("\n📋 Test Users Summary:")
            print("=" * 50)
            for user_data in TEST_USERS:
                print(f"Role: {user_data['role'].upper()}")
                print(f"  Email: {user_data['email']}")
                print(f"  Username: {user_data['username']}")
                print(f"  Password: {user_data['password']}")
                print(f"  Name (AR): {user_data['full_name_ar']}")
                print(f"  Name (EN): {user_data['full_name_en']}")
                print("-" * 30)
            
        except Exception as e:
            print(f"❌ Error creating test users: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_test_users())