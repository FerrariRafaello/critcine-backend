from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from app.core.sanitize import sanitize_text


class ReviewCreate(BaseModel):
    tmdb_movie_id: int
    rating: float = Field(..., ge=0, le=10)
    comment: Optional[str] = Field(None, max_length=500)

    # strip HTML before storing to prevent XSS if the frontend ever renders raw text
    @field_validator("comment", mode="before")
    @classmethod
    def sanitize_comment(cls, v):
        return sanitize_text(v)


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0, le=10)
    comment: Optional[str] = Field(None, max_length=500)

    @field_validator("comment", mode="before")
    @classmethod
    def sanitize_comment(cls, v):
        return sanitize_text(v)


class ReviewOut(BaseModel):
    id: int
    user_id: int
    tmdb_movie_id: int
    rating: float
    comment: Optional[str] = None
    likes: int = 0
    liked_by_me: bool = False
    created_at: datetime


class ReviewOutFull(ReviewOut):
    # extended version used in the feed — includes the author's name
    user_name: str
