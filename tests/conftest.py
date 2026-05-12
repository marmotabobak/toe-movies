import json
import sqlite3
import tempfile
import pytest
from fastapi.testclient import TestClient

import backend.database as db_module
import backend.routers.movies as movies_module
from backend.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_MOVIES = [
    {
        "title": "Крёстный отец",
        "orig_name": "The Godfather",
        "tvoe_url": "/p/krestnyy-otec",
        "year": 1972,
        "duration_min": 175,
        "imdb_id": "tt0068646",
        "rated": "R",
        "genre": "Crime, Drama",
        "director": "Francis Ford Coppola",
        "writer": "Mario Puzo",
        "actors": "Marlon Brando, Al Pacino",
        "plot": "The aging patriarch of an organized crime dynasty...",
        "language": "English",
        "country": "United States",
        "awards": "Won 3 Oscars",
        "poster_url": "https://example.com/godfather.jpg",
        "metascore": 100,
        "imdb_rating": 9.2,
        "imdb_votes": 2000000,
        "rt_score": 97,
        "box_office": "$134,966,411",
        "omdb_response": 1,
        "keywords": '["classic","crime"]',
    },
    {
        "title": "Побег из Шоушенка",
        "orig_name": "The Shawshank Redemption",
        "tvoe_url": "/p/pobeg-iz-shoushenka",
        "year": 1994,
        "duration_min": 142,
        "imdb_id": "tt0111161",
        "rated": "R",
        "genre": "Drama",
        "director": "Frank Darabont",
        "writer": "Stephen King",
        "actors": "Tim Robbins, Morgan Freeman",
        "plot": "Two imprisoned men bond over a number of years...",
        "language": "English",
        "country": "United States",
        "awards": "Nominated for 7 Oscars",
        "poster_url": "https://example.com/shawshank.jpg",
        "metascore": 82,
        "imdb_rating": 9.3,
        "imdb_votes": 2800000,
        "rt_score": 89,
        "box_office": "$16,000,000",
        "omdb_response": 1,
        "keywords": '["prison","drama"]',
    },
    {
        "title": "Тёмный рыцарь",
        "orig_name": "The Dark Knight",
        "tvoe_url": "/p/temnyy-rytsar",
        "year": 2008,
        "duration_min": 152,
        "imdb_id": "tt0468569",
        "rated": "PG-13",
        "genre": "Action, Crime, Drama",
        "director": "Christopher Nolan",
        "writer": "Jonathan Nolan",
        "actors": "Christian Bale, Heath Ledger",
        "plot": "When the menace known as the Joker...",
        "language": "English",
        "country": "United States",
        "awards": "Won 2 Oscars",
        "poster_url": "https://example.com/darkknight.jpg",
        "metascore": 84,
        "imdb_rating": 9.0,
        "imdb_votes": 2700000,
        "rt_score": 94,
        "box_office": "$534,858,444",
        "omdb_response": 1,
        "keywords": '["superhero","action"]',
    },
    {
        "title": "Неизвестный фильм",
        "orig_name": None,
        "tvoe_url": "/p/neizvestnyy-film",
        "year": 2020,
        "duration_min": 90,
        "imdb_id": None,
        "rated": None,
        "genre": None,
        "director": None,
        "writer": None,
        "actors": None,
        "plot": None,
        "language": None,
        "country": None,
        "awards": None,
        "poster_url": None,
        "metascore": None,
        "imdb_rating": None,
        "imdb_votes": None,
        "rt_score": None,
        "box_office": None,
        "omdb_response": 0,
        "keywords": "[]",
    },
]

INSERT_SQL = """
    INSERT INTO movies
        (title, orig_name, tvoe_url, year, duration_min, imdb_id, rated, genre,
         director, writer, actors, plot, language, country, awards, poster_url,
         metascore, imdb_rating, imdb_votes, rt_score, box_office, omdb_response, keywords)
    VALUES
        (:title, :orig_name, :tvoe_url, :year, :duration_min, :imdb_id, :rated, :genre,
         :director, :writer, :actors, :plot, :language, :country, :awards, :poster_url,
         :metascore, :imdb_rating, :imdb_votes, :rt_score, :box_office, :omdb_response, :keywords)
"""

CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS movies (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        title         TEXT NOT NULL,
        orig_name     TEXT,
        tvoe_url      TEXT UNIQUE NOT NULL,
        year          INTEGER,
        duration_min  INTEGER,
        imdb_id       TEXT,
        rated         TEXT,
        genre         TEXT,
        director      TEXT,
        writer        TEXT,
        actors        TEXT,
        plot          TEXT,
        language      TEXT,
        country       TEXT,
        awards        TEXT,
        poster_url    TEXT,
        metascore     INTEGER,
        imdb_rating   REAL,
        imdb_votes    INTEGER,
        rt_score      INTEGER,
        box_office    TEXT,
        omdb_response INTEGER NOT NULL DEFAULT 0,
        keywords      TEXT NOT NULL DEFAULT '[]',
        created_at    TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
    )
"""


@pytest.fixture()
def test_db(tmp_path, monkeypatch):
    """Fresh SQLite DB with sample data, injected into both the db module and the router."""
    db_path = tmp_path / "test.db"

    def make_conn():
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # Create schema + seed data once
    conn = make_conn()
    conn.execute(CREATE_TABLE_SQL)
    conn.executemany(INSERT_SQL, SAMPLE_MOVIES)
    conn.commit()
    conn.close()

    # Patch get_db wherever it's used
    monkeypatch.setattr(db_module, "get_db", make_conn)
    monkeypatch.setattr(movies_module, "get_db", make_conn)

    return make_conn


@pytest.fixture()
def client(test_db):
    return TestClient(app)
