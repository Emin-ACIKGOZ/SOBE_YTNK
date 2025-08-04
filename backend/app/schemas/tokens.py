# backend/app/schemas/tokens.py

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
