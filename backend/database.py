import sqlite3
import os
from pathlib import Path

DB_PATH = Path(os.getenv("TVOE_DB_PATH", str(Path(__file__).parent / "data" / "movies.db")))


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
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
        );
        CREATE INDEX IF NOT EXISTS idx_year        ON movies(year);
        CREATE INDEX IF NOT EXISTS idx_imdb_rating ON movies(imdb_rating);
        CREATE INDEX IF NOT EXISTS idx_rt_score    ON movies(rt_score);
        CREATE INDEX IF NOT EXISTS idx_genre       ON movies(genre);
    """)
    conn.commit()
    conn.close()
