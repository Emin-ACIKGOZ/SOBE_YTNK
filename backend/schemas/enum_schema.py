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

    RECEIVED = "RECEIVED"
    IN_REVIEW = "IN_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class UserRole(str, PyEnum):
    """
    Extensible Enum for user roles.
    """

    HR = "HR"
    APPLICANT = "APPLICANT"


class EmploymentType(str, PyEnum):
    """Defines the types of employment."""

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"


class SeniorityLevel(str, PyEnum):
    """Defines the seniority level of the position."""

    INTERNSHIP = "INTERNSHIP"
    ENTRY_LEVEL = "ENTRY_LEVEL"
    JUNIOR_LEVEL = "JUNIOR_LEVEL"
    MID_LEVEL = "MID_LEVEL"
    SENIOR_LEVEL = "SENIOR_LEVEL"
    DIRECTOR = "DIRECTOR"
    EXECUTIVE = "EXECUTIVE"


class EducationLevel(str, enum.Enum):
    """Defines the level of education."""

    NONE = "None"
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    DOCTORATE = "Doctorate"
