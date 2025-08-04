# backend/app/database/base.py

from sqlalchemy.ext.declarative import declarative_base

# Create a declarative base class. This is what all of our models
# (like User, in your case) will inherit from.
Base = declarative_base()
