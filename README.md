# tvoe-movies

Personal movie database for films scraped from [tvoe.live](https://tvoe.live), enriched with OMDB metadata.

## Features

- Browse 2,900+ movies with filters (genre, year, IMDB rating, Rotten Tomatoes score, keywords)
- Sort by any column
- Add, edit, and delete movies individually or in bulk
- Tag movies with custom keywords; suggestions shown from existing tags

## Stack

- **Backend**: Python / FastAPI + SQLite
- **Frontend**: React + Vite + Tailwind CSS

## Setup

```bash
# Python dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# JS dependencies (root + frontend)
npm install
npm install --prefix frontend

# Import movie data (once)
python -m backend.scripts.import_data
```

Source data is expected at `~/Desktop/tvoe-movies/movies_ratings.json`.

## Running

```bash
# Both servers concurrently (uvicorn :8000 + Vite :5173)
npm run dev
```

Or separately:

```bash
uvicorn backend.main:app --reload --port 8000
npm run dev --prefix frontend
```

## Testing

```bash
# Unit tests
source .venv/bin/activate
pytest tests/ -v

# E2e tests (requires a production build)
npm run build --prefix frontend
pytest tests/e2e/ -v
```

## Production build

```bash
npm run build --prefix frontend
uvicorn backend.main:app --port 8000
```

FastAPI serves the compiled frontend from `frontend/dist/` as a SPA on the same port.
