# backend/app/crud/users.py

from sqlalchemy.orm import Session
from backend.app.models.users import User

def get_user_by_username(db: Session, username: str):
    """
    Retrieves a user from the database by their unique username.
    """
    return db.query(User).filter(User.username == username).first()
def create_user(db: Session, user_data: dict):
    """
    Creates a new user in the database.
    """
    db_user = User(**   user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  