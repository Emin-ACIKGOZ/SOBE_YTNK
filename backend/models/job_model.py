"""
SQLAlchemy model for a Job Posting.

This module defines the JobPosting model,
which represents a job advertisement in the database.
It includes details about the job, such as title, company, required skills,
and its relationship with job applications.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ARRAY, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base
from backend.schemas.enum_schema import SeniorityLevel, EmploymentType


class JobPosting(Base):
    """
    Represents a job posting in the database.

    Attributes:
        job_id (uuid.UUID): Primary key, a unique identifier for the job posting.
        title (str): The title of the job.
        company_name (str): The name of the company offering the job.
        location (str): The location of the job.
        seniority_level (SeniorityLevel): The seniority level of the position.
        employment_type (EmploymentType): The type of employment (e.g., full-time, part-time).
        description (str): A detailed description of the job.
        responsibilities (list): A list of responsibilities for the role.
        qualifications (list): A list of required qualifications.
        required_skills (list): A list of skills required for the job.
        salary (str): The salary range for the position.
        posted_at (datetime): The date and time the job was posted.
        is_active (bool): A flag indicating if the job posting is active.
        applications (relationship): A relationship to the Application model.
    """

    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    seniority_level = Column(Enum(SeniorityLevel), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)
    description = Column(String, nullable=False)
    responsibilities = Column(ARRAY(String), default=[])
    qualifications = Column(ARRAY(String), default=[])
    required_skills = Column(ARRAY(String), default=[])
    salary = Column(String, nullable=True)
    posted_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationship to the Application model
    applications = relationship("Application", back_populates="job")
