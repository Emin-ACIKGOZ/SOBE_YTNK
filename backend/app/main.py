# backend/app/main.py

from fastapi import FastAPI
# from database.base import Base
# from database.session import engine
from api.routers import applications


# Initialize the FastAPI application
app = FastAPI(
    title="MAIN YTNK API",
    version="0.1.0",
    description="An API for tracking job applications."
)

# Include the new authentication router
# app.include_router(auth.router)

# TEMPORARY: Include the test router for authentication verification
# app.include_router(temporary_test.router)
app.include_router(applications.router)

# # This part is for creating tables on startup, good for development
# # In a production environment, you would use migrations (e.g., Alembic)
# @app.on_event("startup")
# def create_tables():
#     Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
