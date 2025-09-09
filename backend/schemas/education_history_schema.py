"""
Pydantic schemas for validating Education History data.

This module defines the data models used for creating and retrieving
individual education history entries, ensuring data integrity and consistency.
"""

import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


# --- Schemas for the Education History model ---


class EducationHistoryBase(BaseModel):
    """
    Base Pydantic schema for Education History, containing common fields.
    """

    degree: str
    institution: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None


class EducationHistoryCreate(EducationHistoryBase):
    """
    Pydantic schema for creating a new Education History entry.

    This schema is used when submitting data to create a new record.
    """


class EducationHistory(EducationHistoryBase):
    """
    Pydantic schema for reading Education History data from the database.
    Includes the database-generated ID and enables ORM mode.
    """

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID
