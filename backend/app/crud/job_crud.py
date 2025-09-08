"""
This module contains the CRUD (Create, Read, Update, Delete) operations
for the JobPosting model, interacting with the database session.
"""

import uuid
from sqlalchemy.orm import Session
from backend.app.models.job_model import JobPosting
from backend.app.schemas.job_schema import JobPostingCreate, JobPostingUpdate


def create_job(db: Session, job: JobPostingCreate):
    """
    Creates a new job posting in the database.
    """
    db_job = JobPosting(job_id=uuid.uuid4(), **job.model_dump(exclude_unset=True))
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job(db: Session, job_id: uuid.UUID):
    """
    Retrieves a single job posting by its ID.
    """
    return db.query(JobPosting).filter(JobPosting.job_id == job_id).first()


def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of all job postings.
    """
    return db.query(JobPosting).offset(skip).limit(limit).all()


def update_job(db: Session, db_job: JobPosting, job_in: JobPostingUpdate):
    """
    Updates an existing job posting.
    """
    update_data = job_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def soft_delete_job(db: Session, db_job: JobPosting):
    """
    'Soft deletes' a job by setting its is_active flag to False.
    """
    db_job.is_active = False
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
