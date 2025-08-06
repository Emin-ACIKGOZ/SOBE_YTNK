# Backend Application

This repository contains the backend API for a job application processing system. It is developed using FastAPI, SQLAlchemy, and PostgreSQL, designed to manage job postings, applicant information, and the processing of job applications.

## Getting Started

This project leverages Docker and Docker Compose for streamlined setup and execution.
Prerequisites

    Docker Desktop: Ensure Docker is installed and operational on your system.

1. Database Setup (PostgreSQL)

The backend service relies on a PostgreSQL database. The docker-compose.yml file defines a db service for this purpose.

### Excerpt from docker-compose.yml
services:
  db:
    image: postgres:17-alpine
    container_name: ytnk_db
    restart: always
    environment:
      - POSTGRES_USER=ytnk_user
      - POSTGRES_PASSWORD=ytnk_password
      - POSTGRES_DB=ytnk_db
    ports:
      - "6059:5432" # Host:Container
    volumes:
      - postgres_data:/var/lib/postgresql/data/

To initiate the PostgreSQL database:

docker-compose up -d db

This command will:

    Retrieve the postgres:17-alpine Docker image if not locally available.

    Create and start a container named ytnk_db.

    Configure the database with the specified user, password, and database name.

    Map the container's PostgreSQL port (5432) to your host's port 6059.

    Establish a Docker volume (postgres_data) to ensure database data persistence across container lifecycles.

2. Backend Application Setup

The docker-compose.yml also defines the backend service.

## Excerpt from docker-compose.yml
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ytnk_backend
    restart: always
    depends_on:
      - db # Ensures DB is ready before backend starts
    ports:
      - "8000:8000" # Host:Container
    volumes:
      - ./backend:/usr/src/app # For live reloading during development
    env_file:
      - ./backend/.env # Loads database connection string etc.
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Prior to running the backend, create a .env file within the backend/ directory to store your database connection string and other environment variables.

backend/.env example:

DATABASE_URL="postgresql://ytnk_user:ytnk_password@db:5432/ytnk_db"

Note: The db in the DATABASE_URL refers to the Docker Compose service name, not localhost, as the backend container connects to the database container within the isolated Docker network.

To build and execute the backend application:

docker-compose up -d backend

This command will:

    Construct the Docker image for the backend using the Dockerfile located in ./backend.

    Launch a container named ytnk_backend.

    Verify the db service is active and healthy before proceeding with backend startup.

    Map the container's API port (8000) to your host's port 8000.

    Mount your local backend source code into the container, facilitating live reloading during development.

    Load environment variables from backend/.env.

## Accessing the API

Upon successful startup of both services, the backend API can be accessed:

    API Documentation (Swagger UI): http://localhost:8000/docs

    API Redoc: http://localhost:8000/redoc

## Design Overview

The backend application is designed with a focus on modularity, maintainability, and scalability, adhering to established best practices for FastAPI applications.
Layered Architecture

The application employs a layered architecture to effectively separate concerns:

    api/routers/: Contains FastAPI APIRouter instances that define the API endpoints (e.g., /applications, /jobs). This layer serves as the external interface for client interactions.

    crud/: Houses Create, Read, Update, and Delete operations. These functions encapsulate all direct database interactions utilizing SQLAlchemy. This layer functions as the data access layer.

    models/: Defines the SQLAlchemy ORM models (Applicant, Application, JobPosting). These Python classes represent the underlying database table schemas and their relationships.

    schemas/: Contains Pydantic models (ApplicantCreate, Application, JobPostingBase, etc.). These are instrumental for:

        Data Validation: Ensuring incoming request data conforms to predefined types and structures.

        Data Serialization: Transforming Python objects (such as ORM model instances) into JSON responses for the API.

        Enums: Centralized definitions for application statuses and educational levels (ApplicationStatus, EducationLevel).

    services/: Designated for complex business logic that extends beyond basic CRUD operations, including LLM processing for resume parsing, ranking algorithms, or authentication mechanisms.

    database/: Manages the database connection, session creation, and fundamental ORM declarations.

## Hybrid Application Model

The Application model incorporates a hybrid data storage strategy to optimize for both flexibility and query performance.

    Rationale: Resumes frequently contain highly variable, semi-structured data (e.g., detailed work experience descriptions, awards, references) alongside structured, consistent data points (e.g., total years of experience, highest degree). A purely relational or entirely schemaless approach presents inherent limitations.

    Implementation:

        Dedicated Columns: Key, predictable fields (e.g., total_years_experience, parsed_skills, highest_education_level) are stored in distinct, indexed columns. This design facilitates rapid and efficient filtering and ranking of applications.

        JSONB Column (parsed_resume_data): The comprehensive, detailed, and variable parsed resume content is stored within a single JSONB column. This provides flexibility to accommodate diverse resume structures without necessitating frequent database schema migrations. It also serves as the authoritative source for complete resume details, particularly beneficial for LLM processing or thorough human review.

## Separate Applicant Model

    Rationale: A single applicant may submit multiple applications over time, potentially for different job postings or even the same job with an updated resume. Storing applicant-specific details (e.g., name, email, LinkedIn URL) directly within each application record would lead to data redundancy and complicate the tracking of an applicant's complete history within the system.

    Implementation: The Applicant model is dedicated to storing unique personal details of an individual. The Application model then establishes a link to the Applicant who submitted it through a foreign key (applicant_id). This approach ensures data normalization and a clear, traceable relationship between applicants and their submissions.

## Pydantic Schemas for Controlled Mutability

    Rationale: Pydantic schemas are employed to enforce data validation and establish clear contracts for API request inputs and response outputs. For update operations, the use of specialized schemas (e.g., ApplicationUpdate) in conjunction with model_config = ConfigDict(exclude_unset=True) enables controlled mutability.

    Implementation: This mechanism ensures that an update operation will only modify the fields explicitly provided in the Pydantic update schema. Consequently, other fields effectively "behave as if final" for that specific operation, despite the underlying database columns not being strictly immutable. This design mitigates unintended data alterations and promotes predictable API behavior.

## Development

    Dependencies: Project dependencies are managed through the requirements.txt file located in the backend/ directory.

    Database Migrations: (Typically handled by tools such as Alembic, not explicitly covered in the current code.)

    Testing: (Testing framework and tests are not yet implemented.)

## License

TBD