from sqlalchemy.orm import Session
from backend.app.models.users import User
from backend.app.schemas.users import UserCreate
from backend.app.core.security import get_password_hash
import uuid


def create_user(db: Session, user: UserCreate):
    """
    Creates a new user with a hashed password.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=uuid.uuid4(),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: uuid.UUID):
    """
    Retrieves a single user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    Retrieves a single user by their username.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a single user by their email address.
    """
    return db.query(User).filter(User.email == email).first()
