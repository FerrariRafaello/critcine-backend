# _ IMPORTS
from typing import Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class PageOut(BaseModel, Generic[T]):
    data: list[T]
    total: int
    limit: int
    offset: int