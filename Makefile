#
# SOBE_YTNK Project Makefile
#
# Targets for managing a split frontend/backend project.
#
# Usage:
#   make help       - Displays this help message.
#   make init       - Sets up development environments (Conda, Poetry, npm dependencies).
#   make run        - Starts the entire project (backend via Docker Compose, frontend dev server).
#   make format     - Automatically formats all code (Black on backend, Prettier on frontend).
#   make lint       - Runs all linters (backend: flake8, frontend: eslint).
#   make clean      - Cleans up build artifacts. Use 'make clean CLEAN_RESUMES=1' to also delete resume files.
#

# --- Variables ---
FRONTEND_DIR := frontend
BACKEND_DIR := backend
RESUMES_DIR := $(BACKEND_DIR)/resumes
DOCKER_COMPOSE_FILE := $(BACKEND_DIR)/docker-compose.yml
CONDA_ENV_NAME := ytnk-dev # The name of your dedicated development environment

# --- Phony Targets ---
.PHONY: lint-backend lint-frontend lint build-backend build-frontend build \
        run-backend run-frontend run stop-backend init \
        format-backend format format-frontend \
        clean-resumes clean-backend clean-frontend clean help

# --- Component Management Targets ---

## 0. Environment Setup

# Consolidated the old 'init-env' into just 'init' and added frontend setup
init: ## Set up the backend Conda environment (Poetry, Black, Flake8) and frontend dependencies (npm install).
	@echo "🌱 Initializing backend environment: $(CONDA_ENV_NAME)..."
	@if ! conda env list | grep -q "$(CONDA_ENV_NAME)"; then \
		conda create -n $(CONDA_ENV_NAME) python=3.10 -y; \
	fi
	@echo "📦 Installing backend dependencies..."
	@conda run --no-capture-output -n $(CONDA_ENV_NAME) pip install poetry==2.1.4
	# Installs main dependencies only (--no-root fix)
	@conda run --no-capture-output -n $(CONDA_ENV_NAME) poetry install --directory $(BACKEND_DIR) --no-root
	# Installs dev tools decoupled from pyproject.toml
	@conda run --no-capture-output -n $(CONDA_ENV_NAME) pip install black flake8
	@echo "📦 Installing frontend dependencies..."
	@cd $(FRONTEND_DIR) && npm install

# ------------------------------------------------------------------------------

## 1. Cleanup and Utility Targets

# Conditional execution target for resumes
clean-resumes:
	@echo "🧹 Clearing files in $(RESUMES_DIR)/..."
	sudo rm -rf $(RESUMES_DIR)/*

clean-backend:
	@echo "🧹 Cleaning up backend cache and artifacts..."
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(BACKEND_DIR)/.pytest_cache

clean-frontend:
	@echo "🧹 Cleaning up frontend build directory..."
	rm -rf $(FRONTEND_DIR)/dist

# Top-level 'clean' target with conditional execution
clean: clean-backend clean-frontend ## Run default cleanup (artifacts, cache, build files). Use CLEAN_RESUMES=1 to delete resume files.
	@if [ "$(CLEAN_RESUMES)" = "1" ]; then \
		$(MAKE) clean-resumes; \
	fi
	@echo "🧹 All cleanup complete."
	@echo "⚠️ Note: This does not stop running containers. Use 'make stop' to stop them."

stop: stop-backend ## Stop running containers.
	@echo "🛑 Stopping frontend development server is done manually (Ctrl+C)."

stop-backend:
	@echo "🛑 Stopping backend containers..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# ------------------------------------------------------------------------------

## 2. Formatting and Linting Targets

format-backend:
	@echo "✍️ Formatting backend files with Black..."
	@conda run --no-capture-output -n $(CONDA_ENV_NAME) black $(BACKEND_DIR)

format-frontend:
	@echo "✍️ Formatting frontend files with Prettier..."
	@cd $(FRONTEND_DIR) && npm run format

format: format-backend format-frontend ## Automatically format both backend (Black) and frontend (Prettier) files.

lint-backend:
	@echo "🔎 Running backend linters (flake8) in $(CONDA_ENV_NAME)..."
	@conda run --no-capture-output -n $(CONDA_ENV_NAME) flake8 $(BACKEND_DIR)

lint-frontend:
	@echo "🔎 Running frontend ESLint check..."
	@cd $(FRONTEND_DIR) && npm run lint

lint: lint-backend lint-frontend ## Run all linters (backend: flake8, frontend: eslint).

# ------------------------------------------------------------------------------

## 3. Building Targets

build-backend: ## Build the production Docker image for the backend.
	@echo "📦 Building backend Docker image..."
	docker build -t sobe-ytnk-backend:latest $(BACKEND_DIR)

build-frontend: ## Build the frontend production assets bundle.
	@echo "📦 Building frontend production bundle..."
	@cd $(FRONTEND_DIR) && npm run build

build: build-backend build-frontend ## Build both components.

# ------------------------------------------------------------------------------

## 4. Running/Development Targets

run-backend:
	@echo "🚀 Starting backend (API and DB) via Docker Compose..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up --build -d

run-frontend:
	@echo "🚀 Starting frontend development server..."
	@cd $(FRONTEND_DIR) && npm run dev

run: run-backend run-frontend ## Start the entire project (backend and frontend).

# ------------------------------------------------------------------------------

## 5. Help Target

# Help menu
help:
	@echo "\nSOBE_YTNK Project Makefile\n"
	@echo "Usage: make <target> [OPTIONS]\n"
	@echo "\033[1mCORE COMMANDS\033[0m"
	@echo "--------------------------------------------------------------------------------"
	@grep -E '^(init|run|format|lint|clean|build|stop):.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

	@echo "\n\033[1mGRANULAR COMMANDS (Used for specific component actions)\033[0m"
	@echo "--------------------------------------------------------------------------------"
	@grep -E '^(clean-|format-|lint-|build-|run-)[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sed 's/$$/ (Not shown in core help)/'

	@echo "\n\033[1mOPTIONS\033[0m"
	@echo "--------------------------------------------------------------------------------"
	@echo "\033[36mCLEAN_RESUMES=1\033[0m When used with 'make clean', deletes files in $(RESUMES_DIR)/ (e.g., make clean CLEAN_RESUMES=1)"
	@echo ""