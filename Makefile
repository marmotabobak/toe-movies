.PHONY: start backend frontend build install import test test-e2e

VENV := .venv/bin

# Start both backend and frontend concurrently
start:
	PATH=$(VENV):$$PATH npm run dev

# Run backend only
backend:
	$(VENV)/uvicorn backend.main:app --reload --port 8000

# Run frontend dev server only
frontend:
	npm run dev --prefix frontend

# Build frontend for production
build:
	npm run build --prefix frontend

# Install all dependencies (Python + JS)
install:
	python3 -m venv .venv
	$(VENV)/pip install -r requirements.txt
	npm install
	npm install --prefix frontend

# Import movie data from source JSON into SQLite
import:
	$(VENV)/python -m backend.scripts.import_data

# Run unit tests
test:
	$(VENV)/pytest tests/ -v --ignore=tests/e2e

# Run e2e tests (builds frontend first)
test-e2e: build
	$(VENV)/pytest tests/e2e/ -v

# Run all tests
test-all: build
	$(VENV)/pytest tests/ -v
