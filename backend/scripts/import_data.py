"""Run once: python backend/scripts/import_data.py"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.database import get_db, init_db

SOURCE = Path("/Users/igor.urvantsev/Desktop/tvoe-movies/movies_ratings.json")


def parse_meta(meta: str) -> dict:
    if not meta:
        return {"year": None, "duration_min": None}
    m = re.match(r"^(\d{4}),\s*(?:(\d+)\s*ч\s*)?(?:(\d+)\s*мин)?", meta)
    if not m:
        return {"year": None, "duration_min": None}
    year = int(m.group(1))
    hours = int(m.group(2) or 0)
    mins = int(m.group(3) or 0)
    return {"year": year, "duration_min": hours * 60 + mins}


def parse_rt(ratings: list) -> int | None:
    for r in ratings or []:
        if r.get("Source") == "Rotten Tomatoes":
            val = r.get("Value", "")
            try:
                return int(val.replace("%", ""))
            except ValueError:
                return None
    return None


def parse_int(val: str) -> int | None:
    if not val or val == "N/A":
        return None
    try:
        return int(val.replace(",", ""))
    except ValueError:
        return None


def parse_float(val: str) -> float | None:
    if not val or val == "N/A":
        return None
    try:
        return float(val)
    except ValueError:
        return None


def main():
    init_db()
    movies = json.loads(SOURCE.read_text())
    conn = get_db()

    insert = """
        INSERT OR IGNORE INTO movies
            (title, orig_name, tvoe_url, year, duration_min,
             imdb_id, rated, genre, director, writer, actors, plot,
             language, country, awards, poster_url,
             metascore, imdb_rating, imdb_votes, rt_score,
             box_office, omdb_response, keywords)
        VALUES
            (:title, :orig_name, :tvoe_url, :year, :duration_min,
             :imdb_id, :rated, :genre, :director, :writer, :actors, :plot,
             :language, :country, :awards, :poster_url,
             :metascore, :imdb_rating, :imdb_votes, :rt_score,
             :box_office, :omdb_response, :keywords)
    """

    rows = []
    for m in movies:
        omdb = m.get("omdb") or {}
        ok = omdb.get("Response") == "True"
        meta = parse_meta(m.get("meta", ""))
        rows.append({
            "title": m.get("title", ""),
            "orig_name": m.get("origName"),
            "tvoe_url": m.get("url", ""),
            "year": meta["year"],
            "duration_min": meta["duration_min"],
            "imdb_id": omdb.get("imdbID") if ok else None,
            "rated": omdb.get("Rated") if ok else None,
            "genre": omdb.get("Genre") if ok else None,
            "director": omdb.get("Director") if ok else None,
            "writer": omdb.get("Writer") if ok else None,
            "actors": omdb.get("Actors") if ok else None,
            "plot": omdb.get("Plot") if ok else None,
            "language": omdb.get("Language") if ok else None,
            "country": omdb.get("Country") if ok else None,
            "awards": omdb.get("Awards") if ok else None,
            "poster_url": omdb.get("Poster") if ok else None,
            "metascore": parse_int(omdb.get("Metascore", "")) if ok else None,
            "imdb_rating": parse_float(omdb.get("imdbRating", "")) if ok else None,
            "imdb_votes": parse_int(omdb.get("imdbVotes", "")) if ok else None,
            "rt_score": parse_rt(omdb.get("Ratings", [])) if ok else None,
            "box_office": omdb.get("BoxOffice") if ok else None,
            "omdb_response": 1 if ok else 0,
            "keywords": "[]",
        })

    with conn:
        cur = conn.executemany(insert, rows)

    total = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    print(f"Done. {total} movies in database (skipped duplicates if re-run).")


if __name__ == "__main__":
    main()
