import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict

# Import enums from your project structure
from app.schemas.enums import ApplicationStatus, EducationLevel

# --- Schemas for the Application model ---

class ApplicationBase(BaseModel):
    """
    Base Pydantic schema for Application, containing fields that are directly
    submitted or extracted and stored in the database.
    """
    resume_file_url: str
    resume_language: str

    # Extracted, Indexed Data for Filtering and Ranking
    total_years_experience: int = 0
    has_bachelors_degree: bool = False
    highest_education_level: EducationLevel
    most_recent_job_title: Optional[str] = None
    most_recent_company: Optional[str] = None
    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    
    # Unstructured Data: The source of truth for all other details
    # Use 'Any' type for JSONB to allow flexible dictionary structure
    parsed_resume_data: Any # This will be a dictionary in Python, mapped to JSONB in DB

class ApplicationCreate(ApplicationBase):
    """
    Pydantic schema for creating a new Application.
    Requires applicant_id and optionally job_id.
    """
    applicant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None

class ApplicationUpdate(BaseModel):
    """
    Pydantic schema for updating an existing Application's status.
    """
    status: Optional[ApplicationStatus] = None

class Application(ApplicationBase):
    """
    Pydantic schema for reading Application data from the database.
    Includes database-generated fields like application_id, status, and application_date.
    Enables ORM mode.
    """
    model_config = ConfigDict(from_attributes=True)
    application_id: uuid.UUID
    applicant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    status: ApplicationStatus
    application_date: datetime
