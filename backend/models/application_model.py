import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ARRAY,
    ForeignKey,
    Float,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from backend.database.base import Base
from backend.schemas.enum_schema import ApplicationStatus


class Application(Base):
    """
    SQLAlchemy model for a job application.

    Attributes:
        application_id (uuid.UUID): Primary key, a unique identifier for the application.
        job_id (uuid.UUID): Foreign key linking to the job posting.
        applicant_id (uuid.UUID): Foreign key linking to the applicant.
        application_date (datetime): The date and time the application was submitted.
        status (str): The current status of the application (e.g., 'received', 'in_review').
        resume_file_path (str): The file path to the applicant's resume.
        resume_language (str): The language of the resume.
        total_years_experience (int): The total years of work experience parsed from the resume.
        parsed_skills (list): A list of skills parsed from the resume.
        certifications (dict): Certifications parsed from the resume stored as JSONB.
        languages (dict): Languages spoken by the applicant, parsed from the resume.
        parsed_resume_data (str): The raw text data parsed from the resume.
        ranking_score (float): The final score calculated by the ranking algorithm.
        job (relationship): Establishes a relationship with the JobPosting model.
        applicant (relationship): Establishes a relationship with the Applicant model.
        work_experience (relationship): Relationship to the WorkExperience model.
        education_history (relationship): Relationship to the EducationHistory model.
    """

    __tablename__ = "applications"

    application_id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    job_id = Column(PG_UUID(as_uuid=True), ForeignKey("jobs.job_id"), nullable=False)
    applicant_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("applicants.applicant_id"), nullable=False
    )
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(
        Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.RECEIVED,
    )
    resume_file_path = Column(String, nullable=False)
    resume_language = Column(String, nullable=True)
    total_years_experience = Column(Integer, nullable=True)
    parsed_skills = Column(ARRAY(String), nullable=True)
    certifications = Column(JSONB, nullable=True)
    languages = Column(JSONB, nullable=True)
    parsed_resume_data = Column(String, nullable=True)
    ranking_score = Column(Float, nullable=True)

    # Relationships
    job = relationship("JobPosting", back_populates="applications")
    applicant = relationship("Applicant", back_populates="applications")

    work_experience = relationship(
        "WorkExperience",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    education_history = relationship(
        "EducationHistory",
        back_populates="application",
        cascade="all, delete-orphan",
    )
