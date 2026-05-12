# _ IMPORTS
from fastapi import APIRouter, Query, Depends
from app.tmdb.schemas import MovieResult, MovieSearchResponse
from app.auth.security import get_current_user_id
from app.tmdb.client import search_movies, get_movie, get_trending, get_now_playing, get_movie_credits, get_movie_videos, get_top_rated, get_watch_providers, discover_movies_by_genre, get_external_ids, get_for_you, get_classics



router=APIRouter(prefix="/v1/tmdb", tags=["TMDB"])


@router.get("/search", response_model=MovieSearchResponse)
def search(
    q:str=Query(..., min_length=1),
    page:int=Query(1,ge=1),
    _:int=Depends(get_current_user_id)
)->MovieSearchResponse:
    return search_movies(q,page)


@router.get("/discover", response_model=MovieSearchResponse)
def discover(
    with_genres: int = Query(..., ge=1),
    page: int = Query(1, ge=1),
    sort_by: str = Query("release_date.desc"),
    _: int = Depends(get_current_user_id),
) -> MovieSearchResponse:
    return discover_movies_by_genre(with_genres, page, sort_by)



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


@router.get("/top-rated", response_model=MovieSearchResponse)
def top_rated(
    _:int=Depends(get_current_user_id)
)-> MovieSearchResponse:
    return get_top_rated()


@router.get("/movies/{movie_id}/providers")
def watch_providers(
    movie_id:int,
    _:int=Depends(get_current_user_id)
)->dict:
    return get_watch_providers(movie_id)


@router.get("/movies/{movie_id}/external-ids")
def external_ids(
    movie_id: int,
    _: int = Depends(get_current_user_id)
) -> dict:
    return get_external_ids(movie_id)


@router.get("/for-you", response_model=MovieSearchResponse)
def for_you(
    genres: str=Query(..., description="Comma-separated genre IDs"),
    _:int=Depends(get_current_user_id)
)-> MovieSearchResponse:
    return get_for_you(genres)


@router.get("/classics", response_model=MovieSearchResponse)
def classics(
    _:int=Depends(get_current_user_id)
)-> MovieSearchResponse:
    return get_classics()
