"""
Pydantic schemas for validating Work Experience data.

This module defines the data models used for creating and retrieving
individual work history entries, ensuring data integrity and consistency.
"""

import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


# --- Schemas for the Work Experience model ---


class WorkExperienceBase(BaseModel):
    """
    Base Pydantic schema for Work Experience, containing common fields.
    """

    job_title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    """
    Pydantic schema for creating a new Work Experience entry.

    This schema is used when submitting data to create a new record.
    """


class WorkExperience(WorkExperienceBase):
    """
    Pydantic schema for reading Work Experience data from the database.
    Includes the database-generated ID and enables ORM mode.
    """

    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID
