import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class Applicant(Base):
    """
    SQLAlchemy ORM model for an applicant.
    """

    __tablename__ = "applicants"

    applicant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    linkedin_profile_url = Column(String, nullable=True)
    github_profile_url = Column(String, nullable=True)
