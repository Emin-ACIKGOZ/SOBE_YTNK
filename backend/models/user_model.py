"""
SQLAlchemy model for a User.

This module defines the User model, which represents a user in the database.
It includes basic user information such as username, email, and password,
as well as their role within the system.
"""

import uuid
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base
from backend.schemas.enum_schema import UserRole


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (uuid.UUID): Primary key, a unique identifier for the user.
        username (str): The user's unique username.
        email (str): The user's unique email address.
        hashed_password (str): The hashed password for the user.
        role (UserRole): The role of the user, defined by the UserRole enum.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)  
