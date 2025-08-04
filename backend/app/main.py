# backend/app/main.py

from fastapi import FastAPI
from app.database.base import Base
from app.database.session import engine
from app.api.routers import auth, temporary_test 


# Initialize the FastAPI application
app = FastAPI(
    title="MAIN YTNK API",
    version="0.1.0",
    description="An API for tracking job applications."
)

# Include the new authentication router
app.include_router(auth.router)

# TEMPORARY: Include the test router for authentication verification
app.include_router(temporary_test.router)

# This part is for creating tables on startup, good for development
# In a production environment, you would use migrations (e.g., Alembic)
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
