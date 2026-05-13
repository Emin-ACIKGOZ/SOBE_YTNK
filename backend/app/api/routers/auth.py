from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.users import UserCreate, UserLogin
from app.schemas.tokens import Token
from app.crud.users import get_user_by_username, create_user
from app.services.auth import create_password_hash, verify_password, create_access_token
from app.models.users import User
import uuid

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    user_data = {
        "id": uuid.uuid4(),
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": create_password_hash(user_in.password),
        "role": user_in.role,
    }
    create_user(db, user_data)
    access_token = create_access_token(data={"sub": user_in.username})
    return Token(access_token=access_token)


@router.post("/token", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, user_in.username)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)
