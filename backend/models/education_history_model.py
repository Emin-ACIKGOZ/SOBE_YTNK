import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend.database.base import Base


class EducationHistory(Base):
    """
    SQLAlchemy model for an education history entry.

    Attributes:
        id (uuid.UUID): Primary key, a unique identifier for the entry.
        application_id (uuid.UUID): Foreign key linking to the parent application.
        degree (str): The degree obtained.
        institution (str): The institution name.
        start_date (str): The start date of the education.
        end_date (str): The end date of the education.
        location (str): The location of the institution.
        application (relationship): Relationship back to the parent Application model.
    """

    __tablename__ = "education_history"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.application_id"),
        nullable=False,
    )
    degree = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Relationship to the parent Application model
    application = relationship("Application", back_populates="education_history")
