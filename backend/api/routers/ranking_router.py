"""
API router for processing and ranking applications.

This module provides endpoints for uploading a PDF resume, parsing it,
persisting the data to the database, calculating a ranking score,
and retrieving ranked applications for a specific job.
"""

import logging
import os
import shutil
import uuid
from typing import List
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.api.api_dependencies import get_db, get_current_active_user
from backend.schemas.application_schema import (
    Application as ApplicationSchema,
    ApplicationCreate,
)
from backend.schemas.user_schema import User as UserSchema
from backend.crud import (
    applicant_crud as crud_applicants,
    application_crud as crud_applications,
    job_crud as crud_jobs,
)
from backend.services.resume_parsing_service import (
    process_and_persist_resume,
)  # <-- Updated import
from backend.services.resume_text_extraction_service import extract_text_from_pdf
from backend.services.application_ranking_service import calculate_ensemble_score

# Create an API router instance
router = APIRouter(prefix="/ranking", tags=["ranking"])
logger = logging.getLogger(__name__)

# Directory to save uploaded resumes
UPLOAD_DIRECTORY = "./resumes"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post(
    "/process/{job_id}",
    response_model=ApplicationSchema,
    status_code=status.HTTP_201_CREATED,
)
async def process_and_rank_resume(
    job_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Accepts a PDF resume, processes it with the LLM, persists the data,
    calculates a ranking score, and returns the new application record.
    """
    job = crud_jobs.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found."
        )

    # 1. Save the uploaded file to a local directory
    unique_filename = f"{uuid.uuid4()}-{file.filename}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except (IOError, OSError) as e:
        logger.error("Failed to save uploaded file: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save resume file.",
        ) from e

    # 2. Extract text from the saved file
    try:
        with open(file_path, "rb") as saved_file:
            raw_text = await extract_text_from_pdf(BytesIO(saved_file.read()))
    except Exception as e:
        logger.error("Error during PDF text extraction: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract text from PDF.",
        ) from e

    # 3. Call the service layer to handle parsing and persistence
    db_application = await process_and_persist_resume(raw_text, file_path, job_id, db)

    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse and persist resume content.",
        )

    # 4. Calculate and store the ranking score
    ranking_score = calculate_ensemble_score(job, db_application)
    crud_applications.update_application_ranking_score(
        db, db_application.application_id, ranking_score
    )

    # Refresh the object to get the updated score before returning
    db.refresh(db_application)
    return db_application


@router.get(
    "/{job_id}",
    response_model=List[ApplicationSchema],
)
async def get_ranked_applications(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Retrieves all applications for a given job, calculates and returns them
    ranked from highest to lowest score.
    """
    job = crud_jobs.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found."
        )

    # Fetch all applications for the specified job
    applications = crud_applications.get_applications_for_job(db, job_id=job_id)

    # Check for and calculate scores if they don't exist
    for app in applications:
        if app.ranking_score is None:
            ranking_score = calculate_ensemble_score(job, app)
            # Use the new CRUD function to update the score
            crud_applications.update_application_ranking_score(
                db, app.application_id, ranking_score
            )
            # The app object needs to be refreshed to reflect the new score
            db.refresh(app)

    # Sort the applications by the calculated score in descending order
    sorted_applications = sorted(
        applications, key=lambda app: app.ranking_score, reverse=True
    )
    return sorted_applications


@router.get("/resume/{application_id}")
async def get_resume_pdf(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Retrieves the original PDF resume file for a given application.
    """
    application = crud_applications.get_application(db, application_id=application_id)
    if not application or not application.resume_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found."
        )

    file_path = application.resume_file_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on disk.",
        )

    return FileResponse(
        file_path, media_type="application/pdf", filename=os.path.basename(file_path)
    )
