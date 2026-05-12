"""
E2E test setup:
  1. Seeds a temp SQLite DB with known movies.
  2. Starts FastAPI (which also serves the built frontend) on port 8001.
  3. All Playwright tests receive `base_url = "http://localhost:8001"`.
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent

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

SEED_MOVIES = [
    ("Побег из Шоушенка",       "The Shawshank Redemption", "/p/shawshank",    1994, 142, "Drama",              "Frank Darabont",        9.3, 89, 82,  '["prison"]'),
    ("Крёстный отец",           "The Godfather",             "/p/godfather",    1972, 175, "Crime, Drama",        "Francis Ford Coppola",  9.2, 97, 100, '["classic","crime"]'),
    ("Тёмный рыцарь",           "The Dark Knight",           "/p/dark-knight",  2008, 152, "Action, Crime, Drama","Christopher Nolan",     9.0, 94, 84,  '["superhero"]'),
    ("Список Шиндлера",         "Schindler's List",          "/p/schindler",    1993, 195, "Biography, Drama",    "Steven Spielberg",      9.0, 98, 98,  '[]'),
    ("Властелин колец: Возвращение короля", "The Lord of the Rings: The Return of the King",
                                             "/p/lotr-rotk",    2003, 201, "Action, Adventure",  "Peter Jackson",         9.0, 95, 94,  '[]'),
    ("Интерстеллар",            "Interstellar",              "/p/interstellar", 2014, 169, "Adventure, Drama",    "Christopher Nolan",     8.7, 72, 74,  '["space","sci-fi"]'),
    ("Матрица",                 "The Matrix",                "/p/matrix",       1999, 136, "Action, Sci-Fi",      "The Wachowskis",        8.7, 83, 73,  '["sci-fi"]'),
    ("Бойцовский клуб",         "Fight Club",                "/p/fight-club",   1999, 139, "Drama",               "David Fincher",         8.8, 79, 66,  '[]'),
    ("Криминальное чтиво",      "Pulp Fiction",              "/p/pulp-fiction", 1994, 154, "Crime, Drama",        "Quentin Tarantino",     8.9, 93, 95,  '[]'),
    ("Форрест Гамп",            "Forrest Gump",              "/p/forrest-gump", 1994, 142, "Drama, Romance",      "Robert Zemeckis",       8.8, 71, 82,  '[]'),
]


@pytest.fixture(scope="session")
def e2e_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("e2e_db") / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(CREATE_TABLE_SQL)
    conn.executemany(
        """INSERT INTO movies (title, orig_name, tvoe_url, year, duration_min,
                               genre, director, imdb_rating, rt_score, metascore,
                               omdb_response, keywords)
           VALUES (?,?,?,?,?,?,?,?,?,?,1,?)""",
        SEED_MOVIES,
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture(scope="session")
def live_server(e2e_db):
    env = {
        **os.environ,
        "TVOE_DB_PATH": str(e2e_db),
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8001", "--log-level", "warning"],
        cwd=str(ROOT),
        env=env,
    )
    # wait for server to be ready
    import urllib.request, urllib.error
    for _ in range(20):
        try:
            urllib.request.urlopen("http://localhost:8001/api/movies?limit=1")
            break
        except (urllib.error.URLError, ConnectionRefusedError):
            time.sleep(0.3)
    else:
        proc.terminate()
        raise RuntimeError("Backend did not start in time")

    yield "http://localhost:8001"

    proc.terminate()
    proc.wait()


@pytest.fixture(autouse=True)
def reset_db(e2e_db):
    """Re-seed the DB before every test so tests are fully independent."""
    conn = sqlite3.connect(str(e2e_db))
    conn.execute("DELETE FROM movies")
    conn.executemany(
        """INSERT INTO movies (title, orig_name, tvoe_url, year, duration_min,
                               genre, director, imdb_rating, rt_score, metascore,
                               omdb_response, keywords)
           VALUES (?,?,?,?,?,?,?,?,?,?,1,?)""",
        SEED_MOVIES,
    )
    conn.commit()
    conn.close()


@pytest.fixture
def page(live_server, page):
    """Navigate to the app root and wait for it to be ready."""
    page.goto(live_server)
    page.wait_for_selector("text=tvoe-movies")
    page.wait_for_selector("table tbody tr")
    return page
