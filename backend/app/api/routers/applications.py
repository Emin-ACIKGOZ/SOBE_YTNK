from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from backend.app.api.dependencies import get_db
from backend.app.crud import applications as crud_applications
from backend.app.schemas import applications as schemas_applications

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post(
    "/",
    response_model=schemas_applications.Application,
    status_code=status.HTTP_201_CREATED,
)
def create_new_application(
    application: schemas_applications.ApplicationCreate, db: Session = Depends(get_db)
):
    """
    Creates a new application for an applicant and a job.
    """
    # Optional: You can add logic here to ensure the applicant and job exist
    # before creating the application.
    return crud_applications.create_application(db=db, application=application)


@router.get("/{application_id}", response_model=schemas_applications.Application)
def read_application(application_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves a single application by its ID.
    """
    db_application = crud_applications.get_application(
        db=db, application_id=application_id
    )
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application


@router.get(
    "/by-applicant/{applicant_id}",
    response_model=List[schemas_applications.Application],
)
def read_applications_by_applicant(
    applicant_id: uuid.UUID, db: Session = Depends(get_db)
):
    """
    Retrieves a list of applications for a specific applicant.
    """
    applications = crud_applications.get_applications_by_applicant(
        db=db, applicant_id=applicant_id
    )
    return applications


@router.put("/{application_id}/status", response_model=schemas_applications.Application)
def update_application_status(
    application_id: uuid.UUID,
    application_in: schemas_applications.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates the status of an application.
    """
    db_application = crud_applications.get_application(
        db=db, application_id=application_id
    )
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return crud_applications.update_application_status(
        db=db, db_application=db_application, status=application_in.status
    )
