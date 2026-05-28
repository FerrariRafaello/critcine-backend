# _ IMPORTS
from pydantic import BaseModel
from typing import Optional

class Genre(BaseModel):
    id:int
    name:str

class MovieResult(BaseModel):
    id:int
    title:str
    overview:str
    # these fields are not always present in TMDB responses
    release_date:Optional[str]=None
    poster_path:Optional[str]=None
    vote_average:float
    genres: Optional[list[Genre]]=None
    runtime:Optional[int]=None


class MovieSearchResponse(BaseModel):
    results:list[MovieResult]
    total_results:int
    total_pages:int


class TrendingPersonResult(BaseModel):
    id: int
    name: str
    profile_path: Optional[str] = None
    known_for_department: str = "Acting"
    trending_direction: str  # "up", "down", "stable", "new"
