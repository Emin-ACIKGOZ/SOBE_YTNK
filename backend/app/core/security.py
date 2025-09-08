"""
Utilities for password hashing and verification.

This module provides functions to securely hash passwords using the bcrypt
algorithm and to verify a plain-text password against a stored hash.
"""

from passlib.context import CryptContext

# Create a CryptContext instance with the desired hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password.
    Returns the hashed password as a string.
    """
    return pwd_context.hash(password)
