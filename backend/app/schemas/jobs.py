# backend/app/schemas/jobs.py

from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

# Import enums from the centralized file
from app.schemas.enums import SeniorityLevel, EmploymentType


class JobPostingBase(BaseModel):
    """Base schema for a job posting, containing all core fields."""

    title: str = Field(..., description="The official title of the job posting.")
    company_name: str = Field(..., description="The name of the company.")
    location: str = Field(
        ..., description="The geographical location of the job, or 'Remote'."
    )
    seniority_level: SeniorityLevel
    employment_type: EmploymentType
    description: str = Field(
        ..., description="A detailed summary of the job and company."
    )
    responsibilities: List[str] = Field(
        ..., description="A list of key responsibilities for the role."
    )
    qualifications: List[str] = Field(
        ...,
        description="A list of formal qualifications like degrees or years of experience.",
    )
    required_skills: List[str] = Field(
        ..., description="A list of specific technical or soft skills."
    )
    salary: Optional[str] = Field(None, description="The salary range.")


class JobPostingCreate(JobPostingBase):
    """Schema for creating a new job posting."""

    pass


class JobPostingUpdate(BaseModel):
    """Schema for updating an existing job posting."""

    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = None
    employment_type: Optional[EmploymentType] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    qualifications: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    salary: Optional[str] = None
    is_active: Optional[bool] = None


class JobPosting(JobPostingBase):
    """
    Schema for a full job posting, including database-generated fields.
    This is used for returning data from the API.
    """

    job_id: uuid.UUID
    posted_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
