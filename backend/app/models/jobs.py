from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

from backend.app.database.base import Base
from backend.app.schemas.enums import SeniorityLevel, EmploymentType


class JobPosting(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    seniority_level = Column(enum.Enum(SeniorityLevel), nullable=False)
    employment_type = Column(enum.Enum(EmploymentType), nullable=False)
    description = Column(String, nullable=False)
    responsibilities = Column(ARRAY(String), default=[])
    qualifications = Column(ARRAY(String), default=[])
    required_skills = Column(ARRAY(String), default=[])
    salary = Column(String, nullable=True)
    posted_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationship to the Application model
    applications = relationship("Application", back_populates="job")
