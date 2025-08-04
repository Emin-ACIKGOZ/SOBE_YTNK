# backend/app/schemas/enums.py

from enum import Enum

class UserRole(str, Enum):
    """
    Extensible Enum for user roles.
    """
    HR = "hr"
    APPLICANT = "applicant"