"""
This module configures and provides a database session for the application.

It sets up the SQLAlchemy engine and a sessionmaker to manage database
interactions, ensuring that each request gets a fresh, isolated session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

# Create a database engine using the DATABASE_URL from your settings.
# The 'pool_pre_ping' argument ensures the connection is still alive.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Use sessionmaker to create a configured Session class.
# This will be the main entry point for all database interactions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
