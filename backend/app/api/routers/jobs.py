# backend/app/api/routers/jobs.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import uuid

# Import dependencies and other project files
from backend.app.api.dependencies import get_db
from backend.app.crud import jobs as crud_jobs
from backend.app.schemas import jobs as schemas_jobs

# Create an API router instance
router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

# Assunming the data is structured, will likely be adjusted to handle raw data or specific formats in the future.
@router.post(
    "/",
    response_model=schemas_jobs.JobPosting,
    status_code=status.HTTP_201_CREATED
)
def create_job_posting(
    job: schemas_jobs.JobPostingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job posting.
    """
    return crud_jobs.create_job_posting(db=db, job=job)


@router.get(
    "/{job_id}",
    response_model=schemas_jobs.JobPosting
)
def read_job_posting(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a single job posting by its ID.
    """
    db_job = crud_jobs.get_job_posting(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    return db_job


@router.get(
    "/",
    response_model=List[schemas_jobs.JobPosting]
)
def read_all_job_postings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all job postings with pagination.
    """
    jobs = crud_jobs.get_all_job_postings(db=db, skip=skip, limit=limit)
    return jobs


@router.put(
    "/{job_id}",
    response_model=schemas_jobs.JobPosting
)
def update_job_posting(
    job_id: uuid.UUID,
    job_update: schemas_jobs.JobPostingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing job posting.
    """
    db_job = crud_jobs.update_job_posting(db=db, job_id=job_id, job_update=job_update)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    return db_job


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_job_posting(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a job posting.
    """
    db_job = crud_jobs.delete_job_posting(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
