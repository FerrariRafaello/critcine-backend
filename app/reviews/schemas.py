# _ IMPORTS
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    tmdb_movie_id:int
    rating:float=Field(..., ge=0, le=10)
    comment:Optional[str]=None


class ReviewUpdate(BaseModel):
    rating:Optional[float]=Field(None, ge=0, le=10)
    comment:Optional[str]=None


class ReviewOut(BaseModel):
    id:int
    user_id:int
    tmdb_movie_id:int
    rating:float
    comment:Optional[str]=None
    likes:int=0
    created_at:datetime
