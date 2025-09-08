# backend/app/api/routers/temporary_test.py

from fastapi import APIRouter, Depends
from backend.app.api.dependencies import get_current_user
from backend.app.models.users import User

# This is a temporary router for testing purposes.
router = APIRouter()

@router.get("/auth-test")
def test_authentication(current_user: User = Depends(get_current_user)):
    """
    A simple protected endpoint to verify the authentication flow.
    """
    return {"message": f"Hello, {current_user.username}! Your authentication is working."}
