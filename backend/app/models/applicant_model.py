"""
SQLAlchemy model for an Applicant.

This module defines the Applicant model, which represents a job applicant in the
database. It includes fields for personal information and a relationship to
the applications they have submitted.
"""

import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.app.database.base import Base


class Applicant(Base):
    """
    Represents a job applicant in the database.

    Attributes:
        applicant_id (UUID): The unique ID of the applicant.
        first_name (str): The applicant's first name.
        last_name (str): The applicant's last name.
        email (str): The applicant's email address (unique).
        phone_number (str): The applicant's phone number.
        linkedin_profile_url (str): The URL to the applicant's LinkedIn profile.
        github_profile_url (str): The URL to the applicant's GitHub profile.
        applications (relationship): A relationship to the Application model.
    """

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
