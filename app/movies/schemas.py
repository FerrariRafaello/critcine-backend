# _ IMPORTS
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional

# _ pydantic Classes
class MovieBase(BaseModel):
    name:Annotated[str, StringConstraints(
        strip_whitespace=True,
        pattern=r'^[A-Za-z ]+$'
    )]=Field(..., min_length=2, max_length=50)
    year:int=Field(..., ge=1800, le=2026)
    rating:Optional[float]=Field(None, ge=0.0, le=10.0)


class CreateMovie(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MoviePatch(BaseModel):
    name:Optional[Annotated[str, StringConstraints(
        strip_whitespace=True,
        pattern=r'^[A-Za-z ]+$'
    )]]=Field(None, min_length=2, max_length=50)
    year:Optional[int]=Field(None, ge=1800, le=2026)
    rating:Optional[float]=Field(None, ge=0.0, le=10.0)


class MovieOut(MovieBase):
    id:int
