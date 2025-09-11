# --------------------
# Stage 1: Build Image
# --------------------
FROM python:3.10-slim AS builder

# Set the working directory to the project root's parent directory.
WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PYTHONUNBUFFERED=1

# Install build-time dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tcl-dev tk-dev \
    && pip install poetry==2.1.4 \
    && rm -rf /var/lib/apt/lists/*

# Navigate to the backend directory for poetry commands.
WORKDIR /app/backend

# Copy only the Poetry files to leverage Docker's layer caching.
COPY poetry.lock pyproject.toml ./

# Install dependencies using Poetry.
RUN poetry install --no-root --only main

# Copy the rest of the application source code.
COPY . .

# --------------------
# Stage 2: Final Image
# --------------------
FROM python:3.10-slim AS final

# Set the working directory to the project root's parent directory.
WORKDIR /app

# Install runtime dependencies needed for the application to run.
# This is the key fix for the ImportError.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libtcl8.6 libtk8.6 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage.
COPY --from=builder /app/backend/.venv /app/.venv

# Copy the entire 'backend' directory, which is now a module, into the final image.
COPY --from=builder /app/backend /app/backend

# Expose the port that the FastAPI application will run on.
EXPOSE 8000

# The command now correctly references the 'backend' module.
CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
