# _ IMPORTS
from fastapi import APIRouter, Query, Depends
from app.tmdb.client import search_movies, get_movie
from app.tmdb.schemas import MovieResult, MovieSearchResponse
from app.auth.security import get_current_user_id


router=APIRouter(prefix="/v1/tmdb", tags=["TMDB"])


@router.get("/search", response_model=MovieSearchResponse)
def search(
    q:str=Query(..., min_length=1),
    page:int=Query(1,ge=1),
    _:int=Depends(get_current_user_id)
)->MovieSearchResponse:
    return search_movies(q,page)


@router.get("/movies/{movie_id}", response_model=MovieResult)
def movie_detail(
    movie_id:int,
    _:int=Depends(get_current_user_id)
)->MovieResult:
    return get_movie(movie_id)
