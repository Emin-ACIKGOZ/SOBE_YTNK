"""
API router for managing job postings.

This module provides endpoints for creating, retrieving, updating,
and soft-deleting job postings.
"""

from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

# Import dependencies and other project files
from backend.api.api_dependencies import get_db, get_current_active_user
from backend.crud import job_crud as crud_jobs
from backend.schemas import job_schema as schemas_jobs
from backend.schemas.user_schema import User as UserSchema

# Create an API router instance with a prefix and tags
router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.post(
    "/", response_model=schemas_jobs.JobPosting, status_code=status.HTTP_201_CREATED
)
def create_job_posting(
    job: schemas_jobs.JobPostingCreate,
    db: Session = Depends(get_db),
    # This dependency ensures only authenticated users can create jobs.
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Create a new job posting.
    """
    return crud_jobs.create_job(db=db, job=job)


@router.get("/{job_id}", response_model=schemas_jobs.JobPosting)
def read_job_posting(job_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single job posting by its ID.
    """
    db_job = crud_jobs.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found"
        )
    return db_job


@router.get("/", response_model=List[schemas_jobs.JobPosting])
def read_all_job_postings(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve a list of all job postings with pagination.
    """
    jobs = crud_jobs.get_jobs(db=db, skip=skip, limit=limit)
    return jobs


@router.put("/{job_id}", response_model=schemas_jobs.JobPosting)
def update_job_posting(
    job_id: uuid.UUID,
    job_update: schemas_jobs.JobPostingUpdate,
    db: Session = Depends(get_db),
    # Only authenticated users should be able to update jobs
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Update an existing job posting.
    """
    db_job = crud_jobs.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found"
        )
    return crud_jobs.update_job(db=db, db_job=db_job, job_in=job_update)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    # Only authenticated users should be able to delete jobs
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Soft deletes a job posting by setting it to inactive.
    """
    db_job = crud_jobs.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found"
        )
    crud_jobs.soft_delete_job(db=db, db_job=db_job)
    # FastAPI returns a 204 No Content response for successful deletion
    return Response(status_code=status.HTTP_204_NO_CONTENT)
