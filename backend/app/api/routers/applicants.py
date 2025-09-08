from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from backend.app.api.dependencies import get_db
from backend.app.crud import applicants as crud_applicants
from backend.app.schemas import applicants as schemas_applicants

router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.post(
    "/",
    response_model=schemas_applicants.Applicant,
    status_code=status.HTTP_201_CREATED,
)
def create_new_applicant(
    applicant: schemas_applicants.ApplicantCreate, db: Session = Depends(get_db)
):
    """
    Creates a new applicant.
    """
    return crud_applicants.create_applicant(db=db, applicant=applicant)


@router.get("/{applicant_id}", response_model=schemas_applicants.Applicant)
def read_applicant(applicant_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves a single applicant by their ID.
    """
    db_applicant = crud_applicants.get_applicant(db=db, applicant_id=applicant_id)
    if not db_applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return db_applicant


@router.get("/", response_model=List[schemas_applicants.Applicant])
def read_applicants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of applicants with pagination.
    """
    applicants = crud_applicants.get_applicants(db=db, skip=skip, limit=limit)
    return applicants


@router.put("/{applicant_id}", response_model=schemas_applicants.Applicant)
def update_applicant(
    applicant_id: uuid.UUID,
    applicant_in: schemas_applicants.ApplicantUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates an existing applicant's information.
    """
    db_applicant = crud_applicants.get_applicant(db=db, applicant_id=applicant_id)
    if not db_applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return crud_applicants.update_applicant(
        db=db, db_applicant=db_applicant, applicant_in=applicant_in
    )


@router.delete("/{applicant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_applicant(applicant_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Deletes an applicant from the database.
    """
    db_applicant = crud_applicants.get_applicant(db=db, applicant_id=applicant_id)
    if not db_applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    crud_applicants.delete_applicant(db=db, db_applicant=db_applicant)
    return
