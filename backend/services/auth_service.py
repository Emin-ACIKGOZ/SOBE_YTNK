"""
Utilities for password hashing, verification, and JWT token management.

This module provides helper functions to securely handle user passwords
and to create and manage JSON Web Tokens for authentication.
"""

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from backend.core.config import settings

# CryptContext for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper functions for password management
def create_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Helper functions for JWT token management
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a new JWT access token.

    Args:
        data: The payload to encode in the token.
        expires_delta: The expiration time for the token.

    Returns:
        The encoded JWT as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# This is a basic implementation. For production, you would also want to handle
# token expiration and potentially refresh tokens.
