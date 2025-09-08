from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from backend.app.database.base import Base
from backend.app.schemas.enums import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(
        UUID(as_uuid=True), ForeignKey("applicants.applicant_id"), nullable=False
    )
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=True)

    resume_file_url = Column(String, nullable=False)
    resume_language = Column(String, nullable=False)

    total_years_experience = Column(Integer, default=0)
    work_history = Column(JSON, default=[])
    education_history = Column(JSON, default=[])

    parsed_skills = Column(JSON, default=[])
    certifications = Column(JSON, default=[])
    languages = Column(JSON, default=[])

    parsed_resume_data = Column(JSON, nullable=True)

    status = Column(String, default=ApplicationStatus.RECEIVED)
    application_date = Column(DateTime, default=datetime.utcnow)

    # Relationship to the Applicant model
    applicant = relationship("Applicant", back_populates="applications")
    job = relationship("JobPosting", back_populates="applications")
