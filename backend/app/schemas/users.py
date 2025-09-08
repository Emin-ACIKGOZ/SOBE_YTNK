# backend/app/schemas/users.py

import uuid
from pydantic import BaseModel, EmailStr, Field
from backend.app.schemas.enums import UserRole


class UserBase(BaseModel):
    """
    Base schema with common user attributes.
    """

    username: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    """
    Schema for creating a new user (used in signup).
    Requires a password and validates its length.
    """

    password: str = Field(..., min_length=8)


class User(UserBase):
    """
    Schema for returning user data.
    This includes the UUID and is used for API responses.
    """

    id: uuid.UUID

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    Uses username instead of email for login.
    """

    username: str
    password: str
