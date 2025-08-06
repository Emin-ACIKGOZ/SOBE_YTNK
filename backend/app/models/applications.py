import uuid
from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime
from app.database.base import Base
from app.schemas.enums import ApplicationStatus, EducationLevel

class Application(Base):
    """
    SQLAlchemy ORM model for a job application.
    Implements the hybrid approach for data storage.
    """
    __tablename__ = "applications"

    # Core Application Metrics
    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("applicants.applicant_id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.job_id"), nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED)
    application_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    resume_file_url = Column(String, nullable=False)
    resume_language = Column(String, nullable=False)

    # Extracted, Indexed Data for Filtering and Ranking
    total_years_experience = Column(Integer, index=True, default=0)
    has_bachelors_degree = Column(Boolean, index=True, default=False)
    highest_education_level = Column(Enum(EducationLevel), index=True, nullable=False)
    most_recent_job_title = Column(String, nullable=True)
    most_recent_company = Column(String, nullable=True)
    parsed_skills = Column(ARRAY(String), index=True, default=[])
    certifications = Column(ARRAY(String), default=[])
    languages = Column(ARRAY(String), default=[])

    # Unstructured Data: The source of truth for all other details
    parsed_resume_data = Column(JSONB, nullable=False)