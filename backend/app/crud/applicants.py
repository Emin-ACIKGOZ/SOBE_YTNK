import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

# Import your SQLAlchemy model
from backend.app.models.applicants import Applicant

# Import your Pydantic schema
from backend.app.schemas.applicants import ApplicantCreate

# --- CRUD Operations for Applicant ---

def get_applicant(db: Session, applicant_id: uuid.UUID) -> Optional[Applicant]:
    """
    Retrieves a single applicant by their ID.
    """
    return db.query(Applicant).filter(Applicant.applicant_id == applicant_id).first()

def get_applicant_by_email(db: Session, email: str) -> Optional[Applicant]:
    """
    Retrieves a single applicant by their email address.
    Useful for checking if an applicant already exists before creating a new one.
    """
    return db.query(Applicant).filter(Applicant.email == email).first()

def create_applicant(db: Session, applicant_in: ApplicantCreate) -> Applicant:
    """
    Creates a new applicant record in the database.
    Args:
        db: The database session.
        applicant_in: Pydantic model containing applicant data for creation.
    Returns:
        The newly created Applicant ORM object.
    """
    db_applicant = Applicant(**applicant_in.model_dump())
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant) # Refresh the object to get any database-generated values (like applicant_id)
    return db_applicant

def delete_applicant(db: Session, applicant_id: uuid.UUID) -> bool:
    """
    Deletes an applicant record from the database.
    Returns True if the applicant was found and deleted, False otherwise.
    Note: Deleting an applicant might require handling associated applications
          (e.g., setting their applicant_id to NULL or deleting them too,
          depending on your database cascade rules).
    """
    db_applicant = get_applicant(db, applicant_id)
    if db_applicant:
        db.delete(db_applicant)
        db.commit()
        return True
    return False
