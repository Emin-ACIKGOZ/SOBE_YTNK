"""
Configuration settings for the application.

This module uses Pydantic's BaseSettings to load environment variables
into a structured object, ensuring all required settings are present.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    DATABASE_URL: str
    SECRET_KEY: str  # New: JWT secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        """
        Pydantic's configuration class to specify settings.
        """

        env_file = ".env"


settings = Settings()
