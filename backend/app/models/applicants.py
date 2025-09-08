from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from backend.app.database.base import Base


class Applicant(Base):
    __tablename__ = "applicants"

    applicant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, nullable=True)
    linkedin_profile_url = Column(String, nullable=True)
    github_profile_url = Column(String, nullable=True)

    # Relationship to the Application model
    applications = relationship("Application", back_populates="applicant")
