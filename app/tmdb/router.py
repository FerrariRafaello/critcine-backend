# _ IMPORTS
from fastapi import APIRouter, Query, Depends
from app.tmdb.schemas import MovieResult, MovieSearchResponse
from app.auth.security import get_current_user_id
from app.tmdb.client import search_movies, get_movie, get_trending, get_now_playing, get_movie_credits, get_movie_videos



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


@router.get("/trending", response_model=MovieSearchResponse)
def trending(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_trending()

@router.get("/now-playing", response_model=MovieSearchResponse)
def now_playing(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_now_playing()


@router.get("/movies/{movie_id}/credits")
def movie_credits(
    movie_id:int,
    _:int=Depends(get_current_user_id)
)->dict:
    return get_movie_credits(movie_id)


@router.get("/movies/{movie_id}/videos")
def movie_videos(
    movie_id:int,
    _:int=Depends(get_current_user_id)
)-> dict:
    return get_movie_videos(movie_id)
