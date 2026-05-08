# _ IMPORTS
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WatchlistCreate(BaseModel):
    tmdb_movie_id:int
    status:str ="want_to_watch"


class WatchlistUpdate(BaseModel):
    status:str


class WatchlistOut(BaseModel):
    id:int
    user_id:int
    tmdb_movie_id:int
    status:str
    created_at:datetime
