"""Tests for all /api/movies endpoints."""
import pytest


# ---------------------------------------------------------------------------
# GET /api/movies  (list + filters + pagination + sort)
# ---------------------------------------------------------------------------

class TestListMovies:
    def test_returns_all_movies(self, client):
        r = client.get("/api/movies")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 4
        assert len(body["data"]) == 4

    def test_pagination(self, client):
        r = client.get("/api/movies?limit=2&page=1")
        assert r.json()["total_pages"] == 2
        assert len(r.json()["data"]) == 2

        r2 = client.get("/api/movies?limit=2&page=2")
        assert len(r2.json()["data"]) == 2

        # page beyond last returns empty
        r3 = client.get("/api/movies?limit=2&page=3")
        assert r3.json()["data"] == []

    def test_search_by_title(self, client):
        r = client.get("/api/movies?q=shawshank")
        assert r.json()["total"] == 1
        assert r.json()["data"][0]["orig_name"] == "The Shawshank Redemption"

    def test_search_by_director(self, client):
        r = client.get("/api/movies?q=Nolan")
        assert r.json()["total"] == 1
        assert r.json()["data"][0]["orig_name"] == "The Dark Knight"

    def test_filter_by_genre(self, client):
        r = client.get("/api/movies?genre=Crime")
        data = r.json()["data"]
        assert all("Crime" in (m["genre"] or "") for m in data)
        assert r.json()["total"] == 2  # Godfather + Dark Knight

    def test_filter_by_year_range(self, client):
        r = client.get("/api/movies?year_from=1990&year_to=2000")
        years = [m["year"] for m in r.json()["data"]]
        assert all(1990 <= y <= 2000 for y in years)
        assert 1994 in years

    def test_filter_by_imdb_min(self, client):
        r = client.get("/api/movies?imdb_min=9.2")
        ratings = [m["imdb_rating"] for m in r.json()["data"]]
        assert all(v >= 9.2 for v in ratings)
        assert r.json()["total"] == 2  # 9.2 and 9.3

    def test_filter_by_rt_min(self, client):
        r = client.get("/api/movies?rt_min=95")
        assert r.json()["total"] == 1
        assert r.json()["data"][0]["rt_score"] == 97

    def test_filter_by_keyword(self, client):
        r = client.get("/api/movies?keyword=classic")
        assert r.json()["total"] == 1
        assert r.json()["data"][0]["orig_name"] == "The Godfather"

    def test_sort_by_imdb_desc(self, client):
        r = client.get("/api/movies?sort=imdb_rating&dir=desc")
        ratings = [m["imdb_rating"] for m in r.json()["data"] if m["imdb_rating"] is not None]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_year_asc(self, client):
        r = client.get("/api/movies?sort=year&dir=asc")
        years = [m["year"] for m in r.json()["data"] if m["year"] is not None]
        assert years == sorted(years)

    def test_invalid_sort_column_falls_back_to_title(self, client):
        # should not crash; unknown sort column defaults to title
        r = client.get("/api/movies?sort=injected_column")
        assert r.status_code == 200

    def test_keywords_returned_as_list(self, client):
        r = client.get("/api/movies?q=Godfather")
        keywords = r.json()["data"][0]["keywords"]
        assert isinstance(keywords, list)
        assert "classic" in keywords


# ---------------------------------------------------------------------------
# GET /api/movies/genres
# ---------------------------------------------------------------------------

class TestGenres:
    def test_returns_sorted_unique_genre_tokens(self, client):
        r = client.get("/api/movies/genres")
        assert r.status_code == 200
        genres = r.json()["genres"]
        assert isinstance(genres, list)
        assert "Drama" in genres
        assert "Crime" in genres
        assert genres == sorted(genres)

    def test_no_duplicates(self, client):
        r = client.get("/api/movies/genres")
        genres = r.json()["genres"]
        assert len(genres) == len(set(genres))


# ---------------------------------------------------------------------------
# GET /api/movies/keywords
# ---------------------------------------------------------------------------

class TestKeywords:
    def test_returns_keywords_list(self, client):
        r = client.get("/api/movies/keywords")
        assert r.status_code == 200
        assert isinstance(r.json()["keywords"], list)

    def test_includes_known_keywords(self, client):
        kws = client.get("/api/movies/keywords").json()["keywords"]
        assert "classic" in kws
        assert "drama" in kws

    def test_frequency_ordering(self, client):
        # Make "popular" appear in 2 movies, "rare" in only 1
        movies = client.get("/api/movies").json()["data"]
        client.put(f"/api/movies/{movies[0]['id']}", json={"keywords": ["popular", "rare"]})
        client.put(f"/api/movies/{movies[1]['id']}", json={"keywords": ["popular"]})
        kws = client.get("/api/movies/keywords").json()["keywords"]
        assert kws.index("popular") < kws.index("rare")

    def test_max_20_results(self, client):
        assert len(client.get("/api/movies/keywords").json()["keywords"]) <= 20

    def test_empty_keywords_not_counted(self, client):
        # 4th seed movie has keywords=[] — should not cause errors or pollute results
        r = client.get("/api/movies/keywords")
        assert r.status_code == 200
        assert "" not in r.json()["keywords"]


# ---------------------------------------------------------------------------
# GET /api/movies/:id
# ---------------------------------------------------------------------------

class TestGetMovie:
    def test_returns_full_record(self, client):
        # get id of Godfather first
        movie_id = client.get("/api/movies?q=Godfather").json()["data"][0]["id"]
        r = client.get(f"/api/movies/{movie_id}")
        assert r.status_code == 200
        m = r.json()
        assert m["orig_name"] == "The Godfather"
        assert m["imdb_rating"] == 9.2
        assert isinstance(m["keywords"], list)

    def test_404_for_missing_id(self, client):
        r = client.get("/api/movies/999999")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/movies  (create)
# ---------------------------------------------------------------------------

class TestCreateMovie:
    def test_creates_movie(self, client):
        r = client.post("/api/movies", json={"title": "Новый фильм", "orig_name": "New Film", "year": 2024})
        assert r.status_code == 201
        m = r.json()
        assert m["title"] == "Новый фильм"
        assert m["year"] == 2024
        assert "id" in m

    def test_created_movie_appears_in_list(self, client):
        client.post("/api/movies", json={"title": "Уникальный", "orig_name": "Unique Film"})
        r = client.get("/api/movies?q=Unique Film")
        assert r.json()["total"] == 1

    def test_keywords_stored_and_returned_as_list(self, client):
        r = client.post("/api/movies", json={"title": "Tagged", "keywords": ["sci-fi", "space"]})
        assert r.json()["keywords"] == ["sci-fi", "space"]

    def test_missing_title_returns_422(self, client):
        r = client.post("/api/movies", json={"year": 2024})
        assert r.status_code == 422

    def test_duplicate_tvoe_url_returns_400(self, client):
        r = client.post("/api/movies", json={"title": "Dup", "tvoe_url": "/p/krestnyy-otec"})
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# PUT /api/movies/:id  (update)
# ---------------------------------------------------------------------------

class TestUpdateMovie:
    def _get_godfather_id(self, client):
        return client.get("/api/movies?q=Godfather").json()["data"][0]["id"]

    def test_updates_single_field(self, client):
        mid = self._get_godfather_id(client)
        r = client.put(f"/api/movies/{mid}", json={"year": 1973})
        assert r.status_code == 200
        assert r.json()["year"] == 1973

    def test_updates_keywords(self, client):
        mid = self._get_godfather_id(client)
        r = client.put(f"/api/movies/{mid}", json={"keywords": ["mafia", "italy"]})
        assert r.json()["keywords"] == ["mafia", "italy"]

    def test_other_fields_unchanged(self, client):
        mid = self._get_godfather_id(client)
        client.put(f"/api/movies/{mid}", json={"year": 1973})
        updated = client.get(f"/api/movies/{mid}").json()
        assert updated["orig_name"] == "The Godfather"
        assert updated["imdb_rating"] == 9.2

    def test_empty_body_returns_400(self, client):
        mid = self._get_godfather_id(client)
        r = client.put(f"/api/movies/{mid}", json={})
        assert r.status_code == 400

    def test_unknown_fields_ignored(self, client):
        mid = self._get_godfather_id(client)
        r = client.put(f"/api/movies/{mid}", json={"injected": "DROP TABLE movies", "year": 1972})
        assert r.status_code == 200
        assert r.json()["year"] == 1972


# ---------------------------------------------------------------------------
# DELETE /api/movies/:id
# ---------------------------------------------------------------------------

class TestDeleteMovie:
    def test_deletes_movie(self, client):
        mid = client.get("/api/movies?q=Godfather").json()["data"][0]["id"]
        r = client.delete(f"/api/movies/{mid}")
        assert r.status_code == 200
        assert r.json()["deleted"] == 1
        assert client.get(f"/api/movies/{mid}").status_code == 404

    def test_delete_reduces_total(self, client):
        mid = client.get("/api/movies?q=Shawshank").json()["data"][0]["id"]
        client.delete(f"/api/movies/{mid}")
        assert client.get("/api/movies").json()["total"] == 3

    def test_delete_nonexistent_returns_zero(self, client):
        r = client.delete("/api/movies/999999")
        assert r.json()["deleted"] == 0


# ---------------------------------------------------------------------------
# POST /api/movies/bulk-delete
# ---------------------------------------------------------------------------

class TestBulkDelete:
    def test_deletes_multiple(self, client):
        movies = client.get("/api/movies").json()["data"]
        ids = [m["id"] for m in movies[:2]]
        r = client.post("/api/movies/bulk-delete", json={"ids": ids})
        assert r.status_code == 200
        assert r.json()["deleted"] == 2
        assert client.get("/api/movies").json()["total"] == 2

    def test_empty_ids_returns_400(self, client):
        r = client.post("/api/movies/bulk-delete", json={"ids": []})
        assert r.status_code == 400

    def test_nonexistent_ids_deleted_zero(self, client):
        r = client.post("/api/movies/bulk-delete", json={"ids": [999998, 999999]})
        assert r.json()["deleted"] == 0


# ---------------------------------------------------------------------------
# POST /api/movies/bulk-edit
# ---------------------------------------------------------------------------

class TestBulkEdit:
    def test_updates_genre_on_multiple(self, client):
        movies = client.get("/api/movies").json()["data"]
        ids = [m["id"] for m in movies[:2]]
        r = client.post("/api/movies/bulk-edit", json={"ids": ids, "patch": {"genre": "Documentary"}})
        assert r.status_code == 200
        assert r.json()["updated"] == 2
        for mid in ids:
            assert client.get(f"/api/movies/{mid}").json()["genre"] == "Documentary"

    def test_overwrites_keywords(self, client):
        movies = client.get("/api/movies").json()["data"]
        ids = [m["id"] for m in movies[:3]]
        client.post("/api/movies/bulk-edit", json={"ids": ids, "patch": {"keywords": ["tag1"]}})
        for mid in ids:
            assert client.get(f"/api/movies/{mid}").json()["keywords"] == ["tag1"]

    def test_empty_ids_returns_400(self, client):
        r = client.post("/api/movies/bulk-edit", json={"ids": [], "patch": {"genre": "X"}})
        assert r.status_code == 400

    def test_empty_patch_returns_400(self, client):
        movies = client.get("/api/movies").json()["data"]
        ids = [m["id"] for m in movies[:1]]
        r = client.post("/api/movies/bulk-edit", json={"ids": ids, "patch": {}})
        assert r.status_code == 400

    def test_unallowed_patch_fields_ignored(self, client):
        movies = client.get("/api/movies").json()["data"]
        ids = [m["id"] for m in movies[:1]]
        # "injected" is not in PATCH_COLUMNS — should be stripped, leaving no valid fields
        r = client.post("/api/movies/bulk-edit", json={"ids": ids, "patch": {"injected": "bad"}})
        assert r.status_code == 400
