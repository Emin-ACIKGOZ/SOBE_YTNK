"""
Pydantic schemas for the Application model and its nested components.

This module defines the data models for validating and structuring
job application data, including nested schemas for work experience,
education, skills, and certifications.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Import enums from your project structure
from backend.app.schemas.enum_schema import ApplicationStatus


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


# --- Schemas for nested data ---
class WorkExperience(BaseModel):
    """
    Schema for a single job entry.
    """

    job_title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None


class EducationHistory(BaseModel):
    """
    Schema for a single education entry.
    """

    degree: str
    institution: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None


# --- Schemas for the Application model ---
class ApplicationBase(BaseModel):
    """
    Base Pydantic schema for Application, containing fields that are directly
    submitted or extracted and stored in the database.
    """

    resume_language: Optional[str] = None  # Make this optional in case LLM fails

    total_years_experience: Optional[int] = None  # Make this optional
    work_history: Optional[List[WorkExperience]] = []
    education_history: Optional[List[EducationHistory]] = []

    parsed_skills: Optional[List[str]] = []
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[LanguageSkill]] = []

    parsed_resume_data: Optional[str] = None  # Change type to string from Any
    status: Optional[ApplicationStatus] = ApplicationStatus.RECEIVED
    ranking_score: Optional[float] = None


class ApplicationCreate(ApplicationBase):
    """
    Pydantic schema for creating a new Application.
    Requires applicant_id and optionally job_id.
    """

    applicant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    resume_file_path: str


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
    resume_file_path: str
