"""
API router for managing job applications.

This module defines the API endpoints for creating, retrieving,
and updating job application data. It also includes endpoints
to manage application status and retrieve applications by applicant.
"""

from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.api_dependencies import get_db, get_current_active_user
from backend.app.crud import application_crud as crud_applications
from backend.app.schemas import application_schema as schemas_applications
from backend.app.schemas.user_schema import User as UserSchema
from backend.app.schemas.enum_schema import ApplicationStatus


router = APIRouter(prefix="/applications", tags=["applications"])


@router.post(
    "/",
    response_model=schemas_applications.Application,
    status_code=status.HTTP_201_CREATED,
)
def create_new_application(
    application: schemas_applications.ApplicationCreate,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Creates a new application for an applicant and a job.
    """
    return crud_applications.create_application(db=db, application=application)


@router.get("/{application_id}", response_model=schemas_applications.Application)
def read_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
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
    applicant_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
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
    new_status: ApplicationStatus,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
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
        db=db, db_application=db_application, status=new_status.value
    )
