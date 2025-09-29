"""
This service module handles the orchestration of recalculating application
ranking scores. It fetches required data from CRUD, executes the core
ranking algorithm, and persists the updated scores back to the database.
"""

from typing import List
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Dependency on CRUD layers (Services are allowed to depend on CRUD)
from backend.crud import application_crud as crud_applications
from backend.crud import job_crud as crud_jobs

# Dependency on the core ranking logic (The Calculator Service)
from backend.services.application_ranking_service import calculate_ensemble_score
from backend.models.application_model import Application


# --- Orchestration Functions ---


def recalculate_single_application_score_service(
    db: Session, application_id: uuid.UUID
) -> Application:
    """
    Orchestrates the recalculation of the ranking score for a single application.
    """
    db_application = crud_applications.get_application(db, application_id)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Fetch the Job Posting using job_crud (data access)
    db_job = crud_jobs.get_job(db, db_application.job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Associated Job Posting not found")

    # 1. Calculation (Calling the Calculator Service)
    # The models must be converted to Pydantic schemas if the ranking service strictly requires them.
    # Assuming `calculate_ensemble_score` can handle the SQLAlchemy model objects since they
    # mirror the schema attributes (or you will pass converted schema objects).
    new_score = calculate_ensemble_score(db_job, db_application)

    # 2. Persistence (Calling CRUD to save the result)
    return crud_applications.update_application_ranking_score(
        db=db, application_id=application_id, ranking_score=new_score
    )


def recalculate_applications_for_job_service(
    db: Session, job_id: uuid.UUID
) -> List[Application]:
    """
    Orchestrates the bulk recalculation for all applications tied to a specific job.
    """
    db_job = crud_jobs.get_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job Posting not found")

    # Fetch applications (data access)
    applications = crud_applications.get_applications_for_job(db, job_id)

    # Calculate and update score on each object
    for app in applications:
        try:
            new_score = calculate_ensemble_score(db_job, app)
            app.ranking_score = new_score
        except Exception as e:
            print(f"Error calculating score for application {app.application_id}: {e}")
            app.ranking_score = 0.0

    # Commit all updates in a single batch (persistence)
    crud_applications.bulk_update_ranking_scores(db, applications)

    # Re-fetch or return the list (depending on required behavior, re-fetching is safer)
    return crud_applications.get_applications_for_job(db, job_id)


def recalculate_all_application_scores_service(db: Session) -> List[Application]:
    """
    Orchestrates the bulk recalculation for ALL applications in the database.
    """
    # Fetch all data needed
    all_applications = crud_applications.get_applications(db, limit=100000)
    all_jobs = crud_jobs.get_jobs(db, limit=100000)
    job_map = {job.job_id: job for job in all_jobs}

    # Calculate and update score on each object
    for app in all_applications:
        db_job = job_map.get(app.job_id)
        if db_job:
            try:
                new_score = calculate_ensemble_score(db_job, app)
                app.ranking_score = new_score
            except Exception as e:
                print(
                    f"Error calculating score for application {app.application_id}: {e}"
                )
                app.ranking_score = 0.0

    # Commit all updates in a single batch (persistence)
    crud_applications.bulk_update_ranking_scores(db, all_applications)

    return crud_applications.get_applications(db)
