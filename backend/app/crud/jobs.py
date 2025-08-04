# backend/app/crud/jobs.py

from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

# Import the ORM model from the models file
from app.models.jobs import JobPosting
# Import the Pydantic schemas from the schemas file
from app.schemas.jobs import JobPostingCreate, JobPostingUpdate


# CRUD Functions for the JobPosting model

def create_job_posting(db: Session, job: JobPostingCreate) -> JobPosting:
    """
    Creates a new job posting in the database.

    Args:
        db: The database session.
        job: A Pydantic model containing the job posting data.

    Returns:
        The newly created JobPosting ORM object.
    """
    db_job = JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job_posting(db: Session, job_id: uuid.UUID) -> Optional[JobPosting]:
    """
    Retrieves a single job posting by its ID.

    Args:
        db: The database session.
        job_id: The UUID of the job posting.

    Returns:
        The JobPosting ORM object, or None if not found.
    """
    return db.query(JobPosting).filter(JobPosting.job_id == job_id).first()


def get_all_job_postings(db: Session, skip: int = 0, limit: int = 100) -> List[JobPosting]:
    """
    Retrieves a list of all job postings with optional pagination.

    Args:
        db: The database session.
        skip: The number of records to skip (for pagination).
        limit: The maximum number of records to return.

    Returns:
        A list of JobPosting ORM objects.
    """
    return db.query(JobPosting).offset(skip).limit(limit).all()


def update_job_posting(db: Session, job_id: uuid.UUID, job_update: JobPostingUpdate) -> Optional[JobPosting]:
    """
    Updates an existing job posting.

    Args:
        db: The database session.
        job_id: The UUID of the job to update.
        job_update: A Pydantic model with the fields to update.

    Returns:
        The updated JobPosting ORM object, or None if the job was not found.
    """
    db_job = get_job_posting(db, job_id)
    if not db_job:
        return None
    
    # Iterate over the update model's fields and set the corresponding attributes
    # on the database object.
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job_posting(db: Session, job_id: uuid.UUID) -> Optional[JobPosting]:
    """
    Deletes a job posting from the database.

    Args:
        db: The database session.
        job_id: The UUID of the job to delete.

    Returns:
        The deleted JobPosting ORM object, or None if the job was not found.
    """
    db_job = get_job_posting(db, job_id)
    if not db_job:
        return None
        
    db.delete(db_job)
    db.commit()
    return db_job

