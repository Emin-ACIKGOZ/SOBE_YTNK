"""
Main entrypoint for the FastAPI application.

This module initializes the FastAPI app and includes all necessary API routers
to expose the application's endpoints.
"""

from fastapi import FastAPI
from backend.app.api.routers import (
    applicant_router,
    application_router,
    auth_router,
    job_router,
    ranking_router,
)

# Initialize the FastAPI application
app = FastAPI(
    title="MAIN YTNK API",
    version="0.1.0",
    description="An API for tracking job applications.",
)

# Include all necessary routers
# You need to import and include all routers for a complete API
app.include_router(application_router.router)
app.include_router(job_router.router)
app.include_router(applicant_router.router)
app.include_router(auth_router.router)
app.include_router(ranking_router.router)  # This is the new router


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
