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

from backend.api.api_dependencies import get_db, get_current_active_user
from backend.crud import application_crud as crud_applications
from backend.services import application_recalculation_service as recalculate_service
from backend.schemas import application_schema as schemas_applications
from backend.schemas.user_schema import User as UserSchema
from backend.schemas.enum_schema import ApplicationStatus


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


@router.get("/", response_model=List[schemas_applications.Application])
def read_all_applications(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieves a list of all applications with pagination.
    """
    applications = crud_applications.get_applications(db=db, skip=skip, limit=limit)
    return applications


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


@router.get(
    "/by-job/{job_id}",
    response_model=List[schemas_applications.Application],
)
def read_applications_for_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Retrieves a list of applications for a specific job ID.
    """
    applications = crud_applications.get_applications_for_job(db=db, job_id=job_id)
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


@router.post(
    "/{application_id}/recalculate-rank",
    response_model=schemas_applications.Application,
)
def recalculate_single_application_rank(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Triggers a recalculation of the ranking score for a single application
    via the service layer.
    """
    return recalculate_service.recalculate_single_application_score_service(
        db=db, application_id=application_id
    )


@router.post(
    "/by-job/{job_id}/recalculate-ranks",
    response_model=List[schemas_applications.Application],
)
def recalculate_applications_for_job_rank(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Triggers a recalculation of the ranking score for ALL applications under a specific job ID
    via the service layer.
    """
    return recalculate_service.recalculate_applications_for_job_service(
        db=db, job_id=job_id
    )


@router.post(
    "/recalculate-all-ranks",
    response_model=List[schemas_applications.Application],
)
def recalculate_all_applications_rank(
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Triggers a recalculation of the ranking score for ALL applications in the database
     via the service layer. (WARNING: This can be a long-running process).
    """
    return recalculate_service.recalculate_all_application_scores_service(db=db)
