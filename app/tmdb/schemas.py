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
    imdb_id:Optional[str]=None


class MovieSearchResponse(BaseModel):
    results:list[MovieResult]
    total_results:int
    total_pages:int
