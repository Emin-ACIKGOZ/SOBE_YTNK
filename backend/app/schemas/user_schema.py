"""
Pydantic schemas for user-related data.

This module defines the data models for user creation, login, and
database retrieval, ensuring data integrity and validation.
"""

import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from backend.app.schemas.enum_schema import UserRole


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

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """

    username: str
    password: str
