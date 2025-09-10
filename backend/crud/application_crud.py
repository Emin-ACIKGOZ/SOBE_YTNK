"""
This module contains the CRUD (Create, Read, Update, Delete) operations
for the Application model, interacting with the database session.
"""

import uuid
from typing import List
from sqlalchemy.orm import Session
from backend.models.application_model import Application
from backend.models.work_experience_model import WorkExperience
from backend.models.education_history_model import EducationHistory
from backend.schemas.application_schema import ApplicationCreate


def create_application(db: Session, application: ApplicationCreate) -> Application:
    """
    Creates a new application record along with its nested work and education history.
    """
    # Create the main Application model instance, converting nested Pydantic models
    db_application = Application(
        job_id=application.job_id,
        applicant_id=application.applicant_id,
        resume_file_path=application.resume_file_path,
        resume_language=application.resume_language,
        total_years_experience=application.total_years_experience,
        parsed_skills=application.parsed_skills,
        # Convert Pydantic objects to dictionaries for JSONB serialization
        certifications=[c.model_dump() for c in application.certifications],
        languages=[l.model_dump() for l in application.languages],
        parsed_resume_data=application.parsed_resume_data,
        status=application.status,
    )

    # Convert Pydantic WorkExperienceCreate schemas to SQLAlchemy models
    work_experiences = [
        WorkExperience(**we.model_dump()) for we in application.work_experience
    ]
    db_application.work_experience = work_experiences

    # Convert Pydantic EducationHistoryCreate schemas to SQLAlchemy models
    education_history = [
        EducationHistory(**eh.model_dump()) for eh in application.education_history
    ]
    db_application.education_history = education_history

    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_application(db: Session, application_id: uuid.UUID) -> Application:
    """
    Retrieves a single application by its ID.
    """
    return (
        db.query(Application)
        .filter(Application.application_id == application_id)
        .first()
    )


def get_applications(db: Session, skip: int = 0, limit: int = 100) -> List[Application]:
    """
    Retrieves a list of all applications.
    """
    return db.query(Application).offset(skip).limit(limit).all()


def get_applications_by_applicant(
    db: Session, applicant_id: uuid.UUID
) -> List[Application]:
    """
    Retrieves a list of applications for a specific applicant.
    """
    return db.query(Application).filter(Application.applicant_id == applicant_id).all()


def get_applications_for_job(db: Session, job_id: uuid.UUID) -> List[Application]:
    """
    Retrieves a list of applications for a specific job.
    """
    return db.query(Application).filter(Application.job_id == job_id).all()


def update_application_status(db: Session, db_application: Application, status: str):
    """
    Updates the status of an application.
    """
    db_application.status = status
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_application_ranking_score(
    db: Session, application_id: uuid.UUID, ranking_score: float
):
    """
    Updates the ranking score for a specific application.
    """
    db_application = get_application(db, application_id)
    if db_application:
        db_application.ranking_score = ranking_score
        db.commit()
        db.refresh(db_application)
        return db_application
    return None
