from sqlalchemy.orm import Session
from backend.app.models.applications import Application
from backend.app.schemas.applications import ApplicationCreate, ApplicationUpdate
import uuid


def create_application(db: Session, application: ApplicationCreate):
    """
    Creates a new application record.
    """
    db_application = Application(
        application_id=uuid.uuid4(), **application.model_dump(exclude_unset=True)
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_application(db: Session, application_id: uuid.UUID):
    """
    Retrieves a single application by its ID.
    """
    return (
        db.query(Application)
        .filter(Application.application_id == application_id)
        .first()
    )


def get_applications_by_applicant(db: Session, applicant_id: uuid.UUID):
    """
    Retrieves a list of applications for a specific applicant.
    """
    return db.query(Application).filter(Application.applicant_id == applicant_id).all()


def update_application_status(db: Session, db_application: Application, status: str):
    """
    Updates the status of an application.
    """
    db_application.status = status
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application
