import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

# Import your SQLAlchemy model
from backend.app.models.applications import Application

# Import your Pydantic schemas
from backend.app.schemas.applications import ApplicationCreate, ApplicationUpdate

# --- CRUD Operations for Application ---

def get_application(db: Session, application_id: uuid.UUID) -> Optional[Application]:
    """
    Retrieves a single application by its ID.
    """
    return db.query(Application).filter(Application.application_id == application_id).first()

def get_applications_by_applicant(db: Session, applicant_id: uuid.UUID) -> List[Application]:
    """
    Retrieves all applications submitted by a specific applicant.
    """
    return db.query(Application).filter(Application.applicant_id == applicant_id).all()

def get_applications_by_job(db: Session, job_id: uuid.UUID) -> List[Application]:
    """
    Retrieves all applications submitted for a specific job posting.
    """
    return db.query(Application).filter(Application.job_id == job_id).all()

def create_application(db: Session, application_in: ApplicationCreate) -> Application:
    """
    Creates a new application record in the database.
    This function expects all required data (including parsed resume data)
    to be present in the application_in Pydantic model.
    Args:
        db: The database session.
        application_in: Pydantic model containing application data for creation.
    Returns:
        The newly created Application ORM object.
    """
    db_application = Application(**application_in.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application) # Refresh to get database-generated values
    return db_application

def update_application_status(db: Session, application_id: uuid.UUID, application_update: ApplicationUpdate) -> Optional[Application]:
    """
    Updates the status of an existing application.
    Args:
        db: The database session.
        application_id: The ID of the application to update.
        application_update: Pydantic model containing the new status.
    Returns:
        The updated Application ORM object, or None if not found.
    """
    db_application = get_application(db, application_id)
    if db_application:
        # Only update fields that are provided in the update schema
        update_data = application_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_application, key, value)
        
        db.add(db_application) # Add back to session for update tracking
        db.commit()
        db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: uuid.UUID) -> bool:
    """
    Deletes an application record from the database.
    Returns True if the application was found and deleted, False otherwise.
    """
    db_application = get_application(db, application_id)
    if db_application:
        db.delete(db_application)
        db.commit()
        return True
    return False
