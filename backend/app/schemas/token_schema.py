"""
Pydantic schemas for API authentication tokens.

This module defines the data models for the JWT tokens used for authentication,
including the token itself and the data contained within its payload.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the token returned upon successful login.
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for the data contained within a JWT.
    """

    username: str | None = None
