import uuid
from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime
from backend.app.database.base import Base
from backend.app.schemas.enums import ApplicationStatus


class Application(Base):
    """
    SQLAlchemy ORM model for a job application.
    Implements the hybrid approach for data storage.
    """

    __tablename__ = "applications"

    # Core Application Metrics
    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(
        UUID(as_uuid=True), ForeignKey("applicants.applicant_id"), nullable=False
    )
    job_id = Column(
        UUID(as_uuid=True), ForeignKey("job_postings.job_id"), nullable=True
    )
    status = Column(
        Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.RECEIVED
    )
    application_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    resume_file_url = Column(String, nullable=False)
    resume_language = Column(String, nullable=False)

    # Extracted, Indexed Data for Filtering and Ranking
    total_years_experience = Column(Integer, index=True, default=0)

    # NEW: Replacing individual fields with structured lists for detailed history
    work_history = Column(JSONB, default=[], nullable=True)
    education_history = Column(JSONB, default=[], nullable=True)

    parsed_skills = Column(ARRAY(String), index=True, default=[])
    certifications = Column(JSONB, default=[])  # CORRECTED LINE
    languages = Column(ARRAY(String), default=[])

    # Unstructured Data: The source of truth for all other details
    parsed_resume_data = Column(JSONB, nullable=False)
