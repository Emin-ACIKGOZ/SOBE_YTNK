# backend/app/models/jobs.py

import uuid
from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
from app.database.base import Base
from app.schemas.enums import SeniorityLevel, EmploymentType


class JobPosting(Base):
    """
    SQLAlchemy ORM model for a job posting.
    This model defines the table structure in the database.
    """

    __tablename__ = "job_postings"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    seniority_level = Column(Enum(SeniorityLevel), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)

    description = Column(String, nullable=False)
    responsibilities = Column(ARRAY(String), nullable=False)

    # Separate fields for filtering and ranking
    qualifications = Column(ARRAY(String), nullable=False)
    required_skills = Column(ARRAY(String), nullable=False)

    salary = Column(String, nullable=True)

    # Metadata fields
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
