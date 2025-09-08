"""
This module defines a set of extensible Enum classes for common job application fields.

These enums provide a clean and type-safe way to handle fixed sets of choices
for application statuses, user roles, employment types, seniority levels,
and education levels.
"""

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


class EmploymentType(str, PyEnum):
    """Defines the types of employment."""

    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"


class SeniorityLevel(str, PyEnum):
    """Defines the seniority level of the position."""

    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry Level"
    ASSOCIATE = "Associate"
    MID_SENIOR_LEVEL = "Mid-Senior Level"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"


class EducationLevel(str, enum.Enum):
    """Defines the level of education."""

    NONE = "None"
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    DOCTORATE = "Doctorate"
