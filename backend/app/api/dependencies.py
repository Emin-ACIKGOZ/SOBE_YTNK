# backend/app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend.app.core.config import settings
from backend.app.database.session import SessionLocal
from backend.app.models.users import User
from backend.app.schemas.tokens import TokenData
from backend.app.crud.users import get_user_by_username  # We will update this CRUD function to be more generic

# The OAuth2PasswordBearer class will handle extracting the token from the
# "Authorization: Bearer <token>" header. The tokenUrl is used by the
# interactive docs UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    """
    Dependency that provides a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    A dependency to get the current authenticated user from a JWT.

    This function is the heart of our auth system. It performs the following steps:
    1.  Uses OAuth2PasswordBearer to get the raw token.
    2.  Decodes the token to get the username.
    3.  Fetches the user from the database.
    4.  Raises an HTTPException if anything fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to get the payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Retrieve the user from the database
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    A dependency that ensures the current user is active.
    This is a good practice for when you add an 'is_active' field to your User model.
    """
    # For now, we will assume all users are active. You would add a check here later.
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user