from fastapi import FastAPI
from app.database.base import Base
from app.database.session import engine
from app.api.routers import auth, jobs, temporary_test


app = FastAPI(
    title="SOBE YTNK API",
    version="0.1.0",
    description="Talent Acquisition & Candidate Scoring API",
)

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(temporary_test.router)

# This part is for creating tables on startup, good for development
# In a production environment, you would use migrations (e.g., Alembic)
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
