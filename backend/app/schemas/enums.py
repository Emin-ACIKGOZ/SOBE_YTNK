# backend/app/schemas/enums.py

from enum import Enum as PyEnum

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
