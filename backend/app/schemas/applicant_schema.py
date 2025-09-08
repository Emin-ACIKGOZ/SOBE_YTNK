"""
Pydantic schemas for validating Applicant data.

This module defines the data models used for creating, updating, and
retrieving Applicant information, ensuring data integrity and consistency.
"""

import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict

# --- Schemas for the Applicant model ---


class ApplicantBase(BaseModel):
    """
    Base Pydantic schema for Applicant, containing common fields.
    """

    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None


class ApplicantCreate(ApplicantBase):
    """
    Pydantic schema for creating a new Applicant.

    Inherits from ApplicantBase.
    """


class ApplicantUpdate(BaseModel):
    """
    Pydantic schema for updating an existing Applicant.

    All fields are optional to allow for partial updates.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    github_profile_url: Optional[str] = None


class Applicant(ApplicantBase):
    """
    Pydantic schema for reading Applicant data from the database.
    Includes the applicant_id and enables ORM mode.
    """

    model_config = ConfigDict(from_attributes=True)
    applicant_id: uuid.UUID
