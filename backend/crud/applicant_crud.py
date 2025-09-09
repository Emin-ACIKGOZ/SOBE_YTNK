"""
This module contains the CRUD (Create, Read, Update, Delete) operations
for the Applicant model, interacting with the database session.
"""

import uuid
from sqlalchemy.orm import Session
from backend.models.applicant_model import Applicant
from backend.schemas.applicant_schema import ApplicantCreate, ApplicantUpdate


def create_applicant(db: Session, applicant: ApplicantCreate):
    """
    Creates a new applicant in the database.
    """
    db_applicant = Applicant(
        applicant_id=uuid.uuid4(), **applicant.model_dump(exclude_unset=True)
    )
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)
    return db_applicant


def get_applicant(db: Session, applicant_id: uuid.UUID):
    """
    Retrieves a single applicant by their ID.
    """
    return db.query(Applicant).filter(Applicant.applicant_id == applicant_id).first()


def get_applicant_by_email(db: Session, email: str):
    """
    Retrieves a single applicant by their email address.
    """
    return db.query(Applicant).filter(Applicant.email == email).first()


def get_applicants(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of applicants.
    """
    return db.query(Applicant).offset(skip).limit(limit).all()


def update_applicant(
    db: Session, db_applicant: Applicant, applicant_in: ApplicantUpdate
):
    """
    Updates an existing applicant's information.
    """
    update_data = applicant_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_applicant, key, value)
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)
    return db_applicant


def delete_applicant(db: Session, db_applicant: Applicant):
    """
    Deletes an applicant from the database.
    """
    db.delete(db_applicant)
    db.commit()
