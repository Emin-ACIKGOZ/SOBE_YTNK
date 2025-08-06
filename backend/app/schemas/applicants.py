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
    pass

class Applicant(ApplicantBase):
    """
    Pydantic schema for reading Applicant data from the database.
    Includes the applicant_id and enables ORM mode.
    """
    model_config = ConfigDict(from_attributes=True)
    applicant_id: uuid.UUID
