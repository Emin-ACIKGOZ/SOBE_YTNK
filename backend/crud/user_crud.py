"""
This module contains the CRUD (Create, Read, Update, Delete) operations
for the User model, interacting with the database session.
"""

import uuid
from sqlalchemy.orm import Session
from backend.models.user_model import User
from backend.schemas.user_schema import UserCreate
from backend.core.security import get_password_hash
from backend.schemas.enum_schema import UserRole


def create_user(db: Session, user: UserCreate):
    """
    Creates a new user with a hashed password.
    """
    hashed_password = get_password_hash(user.password)
    role_enum = UserRole(user.role.upper())

    db_user = User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=role_enum,  # Use the mapped enum value here
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: uuid.UUID):
    """
    Retrieves a single user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    Retrieves a single user by their username.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a single user by their email address.
    """
    return db.query(User).filter(User.email == email).first()
