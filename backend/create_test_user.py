# backend/create_test_user.py

import os
from sqlalchemy.orm import Session
from app.database.base import Base
from app.database.session import engine, SessionLocal
from backend.app.crud.user_crud import create_user
from backend.app.services.auth_service import create_password_hash
from backend.app.models.user_model import User
from backend.app.schemas.enum_schema import UserRole
import uuid

# This script is intended to be run inside the Docker container
# to create a test user for auth testing.

def main():
    print("Creating test user 'testuser' with password 'password123'...")
    db: Session = SessionLocal()
    
    # Check if user already exists to prevent errors on re-run
    existing_user = db.query(User).filter(User.username == "testuser").first()
    if existing_user:
        print("Test user 'testuser' already exists. Skipping creation.")
        db.close()
        return

    try:
        # Create a new user instance
        test_user_data = {
            "id": uuid.uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": create_password_hash("password123"),
            "role": UserRole.HR
        }
        
        # Use your CRUD function to create the user
        create_user(db, test_user_data)
        print("Test user created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist (optional, but good practice for this script)
    Base.metadata.create_all(bind=engine)
    main()

