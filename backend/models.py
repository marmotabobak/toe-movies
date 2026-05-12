from pydantic import BaseModel, Field
from typing import Optional


class MovieBase(BaseModel):
    title: str
    orig_name: Optional[str] = None
    tvoe_url: Optional[str] = None
    year: Optional[int] = None
    duration_min: Optional[int] = None
    imdb_id: Optional[str] = None
    rated: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    writer: Optional[str] = None
    actors: Optional[str] = None
    plot: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    awards: Optional[str] = None
    poster_url: Optional[str] = None
    metascore: Optional[int] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    rt_score: Optional[int] = None
    box_office: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    orig_name: Optional[str] = None
    year: Optional[int] = None
    duration_min: Optional[int] = None
    imdb_id: Optional[str] = None
    rated: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    writer: Optional[str] = None
    actors: Optional[str] = None
    plot: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    awards: Optional[str] = None
    poster_url: Optional[str] = None
    metascore: Optional[int] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    rt_score: Optional[int] = None
    box_office: Optional[str] = None
    keywords: Optional[list[str]] = None


class BulkDeleteRequest(BaseModel):
    ids: list[int]


class BulkEditRequest(BaseModel):
    ids: list[int]
    patch: MovieUpdate
