# backend/app/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.api.dependencies import get_db
from app.crud.users import get_user_by_username
from app.schemas.users import UserLogin
from app.schemas.tokens import Token
from app.services.auth import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns a JWT access token.
    """
    user = get_user_by_username(db, username=form_data.username)

    # Verify if the user exists and the password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create the access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token}
