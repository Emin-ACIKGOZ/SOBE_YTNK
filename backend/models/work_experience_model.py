import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend.database.base import Base


class WorkExperience(Base):
    """
    SQLAlchemy model for a work experience entry.

    Attributes:
        id (uuid.UUID): Primary key, a unique identifier for the entry.
        application_id (uuid.UUID): Foreign key linking to the parent application.
        job_title (str): The job title.
        company (str): The company name.
        start_date (str): The start date of the job.
        end_date (str): The end date of the job.
        description (str): A description of the job responsibilities.
        application (relationship): Relationship back to the parent Application model.
    """

    __tablename__ = "work_experiences"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.application_id"),
        nullable=False,
    )
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # Relationship to the parent Application model
    application = relationship("Application", back_populates="work_experience")
