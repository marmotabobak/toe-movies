import json
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Query
from backend.database import get_db
from backend.models import MovieCreate, MovieUpdate, BulkDeleteRequest, BulkEditRequest

router = APIRouter(prefix="/api/movies", tags=["movies"])

SORT_COLUMNS = {
    "title", "orig_name", "year", "imdb_rating", "rt_score", "metascore", "imdb_votes"
}
PATCH_COLUMNS = {
    "title", "orig_name", "year", "duration_min", "rated", "genre", "director",
    "writer", "actors", "plot", "language", "country", "awards", "poster_url",
    "metascore", "imdb_rating", "imdb_votes", "rt_score", "box_office",
    "imdb_id", "keywords",
}


def _row_to_dict(row) -> dict:
    d = dict(row)
    d["keywords"] = json.loads(d.get("keywords") or "[]")
    return d


@router.get("")
def list_movies(
    q: Optional[str] = None,
    genre: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    imdb_min: Optional[float] = None,
    imdb_max: Optional[float] = None,
    rt_min: Optional[int] = None,
    rt_max: Optional[int] = None,
    keyword: Optional[str] = None,
    sort: str = "title",
    dir: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
):
    sort_col = sort if sort in SORT_COLUMNS else "title"
    sort_dir = "ASC" if dir == "asc" else "DESC"

    where = []
    params = []

    if q:
        where.append("(title LIKE ? OR orig_name LIKE ? OR actors LIKE ? OR director LIKE ?)")
        like = f"%{q}%"
        params += [like, like, like, like]
    if genre:
        where.append("genre LIKE ?")
        params.append(f"%{genre}%")
    if year_from is not None:
        where.append("year >= ?")
        params.append(year_from)
    if year_to is not None:
        where.append("year <= ?")
        params.append(year_to)
    if imdb_min is not None:
        where.append("imdb_rating >= ?")
        params.append(imdb_min)
    if imdb_max is not None:
        where.append("imdb_rating <= ?")
        params.append(imdb_max)
    if rt_min is not None:
        where.append("rt_score >= ?")
        params.append(rt_min)
    if rt_max is not None:
        where.append("rt_score <= ?")
        params.append(rt_max)
    if keyword:
        where.append('keywords LIKE ?')
        params.append(f'%"{keyword}"%')

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    offset = (page - 1) * limit

    conn = get_db()
    total = conn.execute(f"SELECT COUNT(*) FROM movies {where_sql}", params).fetchone()[0]
    rows = conn.execute(
        f"""SELECT id, title, orig_name, year, duration_min, genre, director,
                   imdb_rating, rt_score, metascore, poster_url, imdb_id,
                   omdb_response, keywords, tvoe_url
            FROM movies {where_sql}
            ORDER BY {sort_col} {sort_dir}
            LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ).fetchall()
    conn.close()

    return {
        "data": [_row_to_dict(r) for r in rows],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total + limit - 1) // limit),
    }


@router.get("/genres")
def list_genres():
    conn = get_db()
    rows = conn.execute("SELECT genre FROM movies WHERE genre IS NOT NULL").fetchall()
    conn.close()
    tokens = set()
    for row in rows:
        for g in row["genre"].split(","):
            g = g.strip()
            if g:
                tokens.add(g)
    return {"genres": sorted(tokens)}


@router.get("/keywords")
def list_keywords():
    conn = get_db()
    rows = conn.execute(
        """SELECT value AS keyword, COUNT(*) AS cnt
           FROM movies, json_each(keywords)
           WHERE json_valid(keywords) AND json_array_length(keywords) > 0
           GROUP BY value
           ORDER BY cnt DESC
           LIMIT 20"""
    ).fetchall()
    conn.close()
    return {"keywords": [row["keyword"] for row in rows]}


@router.get("/{movie_id}")
def get_movie(movie_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return _row_to_dict(row)


@router.post("", status_code=201)
def create_movie(body: MovieCreate):
    import uuid
    tvoe_url = body.tvoe_url or f"/manual/{uuid.uuid4().hex[:8]}"
    conn = get_db()
    try:
        cur = conn.execute(
            """INSERT INTO movies
               (title, orig_name, tvoe_url, year, duration_min, imdb_id, rated, genre,
                director, writer, actors, plot, language, country, awards, poster_url,
                metascore, imdb_rating, imdb_votes, rt_score, box_office, keywords)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (body.title, body.orig_name, tvoe_url, body.year, body.duration_min,
             body.imdb_id, body.rated, body.genre, body.director, body.writer,
             body.actors, body.plot, body.language, body.country, body.awards,
             body.poster_url, body.metascore, body.imdb_rating, body.imdb_votes,
             body.rt_score, body.box_office, json.dumps(body.keywords)),
        )
        conn.commit()
        movie_id = cur.lastrowid
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


@router.put("/{movie_id}")
def update_movie(movie_id: int, body: MovieUpdate):
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="Nothing to update")

    safe = {k: v for k, v in data.items() if k in PATCH_COLUMNS}
    if "keywords" in safe:
        safe["keywords"] = json.dumps(safe["keywords"])

    set_clauses = ", ".join(f"{k} = ?" for k in safe)
    values = list(safe.values()) + [movie_id]

    conn = get_db()
    conn.execute(
        f"UPDATE movies SET {set_clauses}, updated_at = datetime('now') WHERE id = ?",
        values,
    )
    conn.commit()
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return _row_to_dict(row)


@router.delete("/{movie_id}")
def delete_movie(movie_id: int):
    conn = get_db()
    cur = conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()
    return {"deleted": cur.rowcount}


@router.post("/bulk-delete")
def bulk_delete(body: BulkDeleteRequest):
    if not body.ids:
        raise HTTPException(status_code=400, detail="ids required")
    placeholders = ",".join("?" * len(body.ids))
    conn = get_db()
    cur = conn.execute(f"DELETE FROM movies WHERE id IN ({placeholders})", body.ids)
    conn.commit()
    conn.close()
    return {"deleted": cur.rowcount}


@router.post("/bulk-edit")
def bulk_edit(body: BulkEditRequest):
    if not body.ids:
        raise HTTPException(status_code=400, detail="ids required")
    data = body.patch.model_dump(exclude_none=True)
    safe = {k: v for k, v in data.items() if k in PATCH_COLUMNS}
    if not safe:
        raise HTTPException(status_code=400, detail="No valid patch fields")
    if "keywords" in safe:
        safe["keywords"] = json.dumps(safe["keywords"])

    set_clauses = ", ".join(f"{k} = ?" for k in safe)
    placeholders = ",".join("?" * len(body.ids))
    values = list(safe.values()) + body.ids

    conn = get_db()
    cur = conn.execute(
        f"UPDATE movies SET {set_clauses}, updated_at = datetime('now') WHERE id IN ({placeholders})",
        values,
    )
    conn.commit()
    conn.close()
    return {"updated": cur.rowcount}
