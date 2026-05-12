# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
# Activate virtualenv (required for all Python commands)
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Import movie data from source JSON into SQLite (run once after setup)
python -m backend.scripts.import_data

# Run backend dev server (port 8000, auto-reload)
uvicorn backend.main:app --reload --port 8000

# Run unit + parse tests
pytest tests/ -v

# Run a single test file or test
pytest tests/test_api.py -v
pytest tests/test_api.py::TestListMovies::test_search_by_title -v

# Run e2e tests (requires built frontend — see below)
pytest tests/e2e/ -v
```

### Frontend
```bash
# Install JS dependencies
npm install --prefix frontend

# Run Vite dev server (port 5173, proxies /api → localhost:8000)
npm run dev --prefix frontend

# Build for production (output to frontend/dist/, served by FastAPI)
npm run build --prefix frontend
```

### Run both together
```bash
npm install          # installs root `concurrently`
npm run dev          # starts uvicorn + vite concurrently
```

## Architecture

### Data flow
Source data lives at `~/Desktop/tvoe-movies/movies_ratings.json` (2,931 movies scraped from tvoe.live with OMDB enrichment). `backend/scripts/import_data.py` parses and loads it into SQLite once. The app never reads the JSON at runtime.

### Backend (`backend/`)
- **`database.py`** — SQLite singleton via `get_db()`. DB path defaults to `backend/data/movies.db`; overridable via `TVOE_DB_PATH` env var (used by e2e tests to inject a temp DB).
- **`main.py`** — FastAPI app entry point. Calls `init_db()` on startup. If `frontend/dist/` exists, mounts it as static files and adds a SPA fallback route, so one `uvicorn` process serves both API and frontend in production.
- **`routers/movies.py`** — All API routes under `/api/movies`. Sort column is whitelisted against `SORT_COLUMNS`; patch fields against `PATCH_COLUMNS` to prevent injection. `keywords` column is stored as a JSON text string (`'["tag1","tag2"]'`) and parsed/serialised at the API boundary via `_row_to_dict()`.
- **`models.py`** — Pydantic models. `MovieUpdate` has all fields optional (partial update). `BulkEditRequest` wraps a `MovieUpdate` patch applied to a list of IDs.

### Frontend (`frontend/src/`)
- **`App.jsx`** — Owns all filter/sort/page state and the `refetchKey` integer. Incrementing `refetchKey` after any mutation triggers a re-fetch in `useMovies`.
- **`hooks/useMovies.js`** — Fetches the movie list. Uses JSON-stringified filters + refetchKey as a cache key to avoid redundant requests.
- **`store/selectionStore.jsx`** — React context holding a `Set` of selected movie IDs. Consumed by `BulkBar` and every `MovieRow` checkbox.
- **`api/movies.js`** — All `fetch` wrappers. During dev, Vite proxies `/api` to `localhost:8000`. In production, requests go to the same FastAPI origin.

### Testing

**Unit tests** (`tests/`) use FastAPI `TestClient` + monkeypatching. `tests/conftest.py` patches `backend.routers.movies.get_db` (the import site) with a function returning connections to a per-test temp SQLite DB — necessary because routes call `get_db()` directly rather than via FastAPI `Depends`.

**E2e tests** (`tests/e2e/`) use `pytest-playwright` (Python). `tests/e2e/conftest.py` seeds a temp SQLite DB, spawns a real `uvicorn` process on port 8001 with `TVOE_DB_PATH` pointing to it, and waits for the server to respond before handing control to tests. The `reset_db` fixture (autouse, function scope) truncates and re-seeds the DB before every test so tests are fully independent despite sharing one server process. Requires a built frontend (`npm run build --prefix frontend`) because FastAPI serves `frontend/dist/` as the SPA.
