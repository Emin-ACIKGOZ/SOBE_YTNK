"""
This module provides the base class for all SQLAlchemy models in the application.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a declarative base class. This is what all of the models
# (like User, for example) will inherit from.
Base = declarative_base()
