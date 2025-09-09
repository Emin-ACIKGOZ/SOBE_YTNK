import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Import enums from your project structure
from backend.schemas.enum_schema import ApplicationStatus

# Import new schemas for work and education history
from backend.schemas.work_experience_schema import WorkExperienceCreate, WorkExperience
from backend.schemas.education_history_schema import (
    EducationHistoryCreate,
    EducationHistory,
)


# --- Pydantic model for Language Skills ---
class LanguageSkill(BaseModel):
    """
    Schema for a language skill entry.
    """

    name: str
    level: Optional[str] = None


# --- Pydantic model for Certifications ---
class Certification(BaseModel):
    """
    Schema for a certification entry.
    """

    name: str
    year_issued: Optional[str] = None
    issuing_organization: Optional[str] = None


# --- Schemas for the Application model ---
class ApplicationBase(BaseModel):
    """
    Base Pydantic schema for Application, containing fields that are directly
    submitted or extracted and stored in the database.
    """

    resume_language: Optional[str] = None
    total_years_experience: Optional[int] = None
    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[LanguageSkill]] = []
    parsed_resume_data: Optional[str] = None
    status: Optional[ApplicationStatus] = ApplicationStatus.RECEIVED
    ranking_score: Optional[float] = None


class ApplicationCreate(ApplicationBase):
    """
    Pydantic schema for creating a new Application.
    This schema is used for inbound data and correctly uses the *Create
    schemas for nested objects that do not have database IDs yet.
    """

    applicant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    resume_file_path: str
    work_history: Optional[List[WorkExperienceCreate]] = []
    education_history: Optional[List[EducationHistoryCreate]] = []


class ApplicationUpdate(BaseModel):
    """
    Pydantic schema for updating an existing Application's status.
    """

    status: Optional[ApplicationStatus] = None


class Application(ApplicationBase):
    """
    Pydantic schema for reading Application data from the database.
    This schema uses the full schemas for nested objects because they will
    have IDs after being saved to the database.
    """

    model_config = ConfigDict(from_attributes=True)
    application_id: uuid.UUID
    applicant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    status: ApplicationStatus
    application_date: datetime
    resume_file_path: str
    work_history: Optional[List[WorkExperience]] = []
    education_history: Optional[List[EducationHistory]] = []
