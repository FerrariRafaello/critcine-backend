# _ IMPORTS
import os
from fastapi import APIRouter, Query, Depends, Request

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.tmdb.schemas import MovieResult, MovieSearchResponse
from app.auth.security import get_current_user_id
from app.tmdb.client import (
    search_movies, get_movie, get_trending, get_now_playing,
    get_movie_credits, get_movie_videos, get_top_rated, get_watch_providers,
    discover_movies_by_genre, get_for_you, get_classics,
    get_animation, get_top10_today, get_movies_by_provider, get_available_providers
)


router = APIRouter(prefix="/v1/tmdb", tags=["TMDB"])
limiter = Limiter(key_func=get_remote_address)


def get_search_limit() -> str:
    return "1000/minute" if os.getenv("TESTING") else "30/minute"


@router.get("/search", response_model=MovieSearchResponse)
@limiter.limit(get_search_limit)
def search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1, le=500),
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return search_movies(q, page)


@router.get("/discover", response_model=MovieSearchResponse)
@limiter.limit(get_search_limit)
def discover(
    request: Request,
    with_genres: int = Query(..., ge=1),
    page: int = Query(1, ge=1, le=500),
    sort_by: str = Query("release_date.desc"),
    _: int = Depends(get_current_user_id),
) -> MovieSearchResponse:
    return discover_movies_by_genre(with_genres, page, sort_by)


@router.get("/movies/{movie_id}", response_model=MovieResult)
def movie_detail(
    movie_id: int,
    _: int = Depends(get_current_user_id)
) -> MovieResult:
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


@router.get("/top10-today", response_model=MovieSearchResponse)
def top10_today(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_top10_today()


@router.get("/movies/{movie_id}/credits")
def movie_credits(
    movie_id: int,
    _: int = Depends(get_current_user_id)
) -> dict:
    return get_movie_credits(movie_id)


@router.get("/movies/{movie_id}/videos")
def movie_videos(
    movie_id: int,
    _: int = Depends(get_current_user_id)
) -> dict:
    return get_movie_videos(movie_id)


@router.get("/top-rated", response_model=MovieSearchResponse)
def top_rated(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_top_rated()


@router.get("/movies/{movie_id}/providers")
def watch_providers(
    movie_id: int,
    _: int = Depends(get_current_user_id)
) -> dict:
    return get_watch_providers(movie_id)


@router.get("/for-you", response_model=MovieSearchResponse)
def for_you(
    genres: str = Query(..., description="Comma-separated genre IDs", max_length=200),
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_for_you(genres)


@router.get("/providers")
def providers(_: int = Depends(get_current_user_id)) -> list:
    return get_available_providers()


@router.get("/providers/{provider_id}/movies", response_model=MovieSearchResponse)
def movies_by_provider(
    provider_id: int,
    page: int = Query(1, ge=1, le=500),
    with_genres: int = Query(None, ge=1),
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_movies_by_provider(provider_id, page, with_genres)


@router.get("/classics", response_model=MovieSearchResponse)
def classics(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_classics()


@router.get("/animation", response_model=MovieSearchResponse)
def animation(
    _: int = Depends(get_current_user_id)
) -> MovieSearchResponse:
    return get_animation()
