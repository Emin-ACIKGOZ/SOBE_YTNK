"""
API router for user authentication and registration.

This module handles user login to issue access tokens and provides an
endpoint for new user registration.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.api_dependencies import get_db
from backend.crud.user_crud import get_user_by_username
from backend.core.security import verify_password
from backend.core.config import settings
from backend.schemas.token_schema import Token
from backend.services.auth_service import create_access_token
from backend.schemas.user_schema import UserCreate, User as UserSchema
from backend.crud import user_crud as crud_users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns an access token.
    """
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def signup_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    db_user = crud_users.get_user_by_username(db, username=user_in.username)

    if db_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    db_user = crud_users.create_user(db=db, user=user_in)
    return db_user
