# backend/app/schemas/enums.py

from enum import Enum as PyEnum
import enum

class ApplicationStatus(str, PyEnum):
    """
    Defines the possible statuses for a job application.
    """
    RECEIVED = "received"
    IN_REVIEW = "in_review"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"


class UserRole(str, PyEnum):
    """
    Extensible Enum for user roles.
    """
    HR = "hr"
    APPLICANT = "applicant"

class EmploymentType(PyEnum):
    """Defines the types of employment."""
    full_time = "Full-time"
    part_time = "Part-time"
    contract = "Contract"
    internship = "Internship"

class SeniorityLevel(PyEnum):
    """Defines the seniority level of the position."""
    internship = "Internship"
    entry_level = "Entry Level"
    associate = "Associate"
    mid_senior_level = "Mid-Senior Level"
    director = "Director"
    executive = "Executive"

class EducationLevel(enum.Enum):
    NONE = "None"
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    DOCTORATE = "Doctorate"