# _ IMPORTS
from pydantic import BaseModel
from typing import Optional


class MovieResult(BaseModel):
    id:int
    title:str
    overview:str
    release_date:Optional[str]=None
    poster_path:Optional[str]=None
    vote_average:float


class MovieSearchResponse(BaseModel):
    results:list[MovieResult]
    total_results:int
    total_pages:int
