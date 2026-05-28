# _ IMPORTS
import atexit
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.tmdb.schemas import MovieResult, MovieSearchResponse, TrendingPersonResult


BASE_URL = "https://api.themoviedb.org/3"
_TIMEOUT = 10.0

# Module-level persistent client - connection pooling + keep-alive across all requests
_http = httpx.Client(timeout=_TIMEOUT)
atexit.register(_http.close)

# TTL cache (thread-safe)
_cache: dict[str, tuple[object, float]] = {}
_lock = threading.Lock()


def _cache_get(key: str) -> Any:
    with _lock:
        e = _cache.get(key)
        return e[0] if e and time.monotonic() < e[1] else None


def _cache_set(key: str, value: object, ttl: float) -> None:
    with _lock:
        _cache[key] = (value, time.monotonic() + ttl)


def _fetch_pages(url: str, base_params: dict, pages: range) -> list[MovieResult]:
    seen_ids: set[int] = set()
    results: list[MovieResult] = []

    def _get(page: int) -> list[dict]:
        resp = _http.get(url, params={**base_params, "page": page})
        resp.raise_for_status()
        return resp.json()["results"]

    with ThreadPoolExecutor(max_workers=len(pages)) as pool:
        for page_movies in pool.map(_get, pages):
            for m in page_movies:
                if m["id"] not in seen_ids:
                    seen_ids.add(m["id"])
                    results.append(MovieResult(**m))
    return results


def search_movies(query: str, page: int = 1) -> MovieSearchResponse:
    key = f"search:{query}:{page}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/search/movie",
        params={"api_key": settings.TMDB_API_KEY, "query": query, "page": page, "language": "pt-BR"},
    )
    resp.raise_for_status()
    result = MovieSearchResponse(**resp.json())
    _cache_set(key, result, 3_600)  # 1h
    return result


def get_movie(movie_id: int) -> MovieResult:
    key = f"movie:{movie_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/movie/{movie_id}",
        params={"api_key": settings.TMDB_API_KEY, "language": "pt-BR"},
    )
    resp.raise_for_status()
    result = MovieResult(**resp.json())
    _cache_set(key, result, 604_800)  # 7 dias
    return result


def get_trending() -> MovieSearchResponse:
    cached = _cache_get("trending")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/trending/movie/week",
        {"api_key": settings.TMDB_API_KEY, "language": "pt-br"},
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies, total_results=len(movies), total_pages=1)
    _cache_set("trending", result, 21_600)  # 6h
    return result


def get_now_playing() -> MovieSearchResponse:
    cached = _cache_get("now_playing")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/movie/now_playing",
        {"api_key": settings.TMDB_API_KEY, "language": "pt-br"},
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies, total_results=len(movies), total_pages=1)
    _cache_set("now_playing", result, 21_600)  # 6h
    return result


def get_movie_credits(movie_id: int) -> dict:
    key = f"credits:{movie_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/movie/{movie_id}/credits",
        params={"api_key": settings.TMDB_API_KEY, "language": "pt-br"},
    )
    resp.raise_for_status()
    result = resp.json()
    _cache_set(key, result, 604_800)  # 7 dias
    return result


def get_movie_videos(movie_id: int) -> dict:
    key = f"videos:{movie_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/movie/{movie_id}/videos",
        params={"api_key": settings.TMDB_API_KEY, "language": "pt-br"},
    )
    resp.raise_for_status()
    result = resp.json()
    _cache_set(key, result, 604_800)  # 7 dias
    return result


def get_top_rated() -> MovieSearchResponse:
    cached = _cache_get("top_rated")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/movie/top_rated",
        {"api_key": settings.TMDB_API_KEY, "language": "pt-BR"},
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies, total_results=len(movies), total_pages=1)
    _cache_set("top_rated", result, 43_200)  # 12h
    return result


def get_watch_providers(movie_id: int) -> dict:
    key = f"watch_providers:{movie_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/movie/{movie_id}/watch/providers",
        params={"api_key": settings.TMDB_API_KEY},
    )
    resp.raise_for_status()
    result = resp.json()
    _cache_set(key, result, 604_800)  # 7 dias
    return result


def discover_movies_by_genre(
    genre_id: int,
    page: int = 1,
    sort_by: str = "release_date.desc",
) -> MovieSearchResponse:
    key = f"discover:{genre_id}:{page}:{sort_by}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/discover/movie",
        params={
            "api_key": settings.TMDB_API_KEY,
            "with_genres": genre_id,
            "sort_by": sort_by,
            "page": page,
            "language": "pt-BR",
            "include_adult": "false",
            "vote_count.gte": 20,
        },
    )
    resp.raise_for_status()
    result = MovieSearchResponse(**resp.json())
    _cache_set(key, result, 7_200)  # 2h
    return result


def get_for_you(genres: str) -> MovieSearchResponse:
    key = f"for_you:{genres}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/discover/movie",
        {
            "api_key": settings.TMDB_API_KEY,
            "language": "pt-BR",
            "with_genres": genres.replace(",", "|"),
            "sort_by": "popularity.desc",
            "vote_count.gte": 100,
        },
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies[:35], total_results=len(movies), total_pages=1)
    _cache_set(key, result, 7_200)  # 2h
    return result


def get_classics() -> MovieSearchResponse:
    cached = _cache_get("classics")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/discover/movie",
        {
            "api_key": settings.TMDB_API_KEY,
            "language": "pt-BR",
            "sort_by": "vote_count.desc",
            "primary_release_date.lte": "1990-12-31",
            "vote_average.gte": 7.0,
        },
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies[:35], total_results=len(movies), total_pages=1)
    _cache_set("classics", result, 86_400)  # 24h
    return result


def get_animation() -> MovieSearchResponse:
    cached = _cache_get("animation")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/discover/movie",
        {
            "api_key": settings.TMDB_API_KEY,
            "language": "pt-BR",
            "with_genres": 16,
            "sort_by": "popularity.desc",
            "vote_count.gte": 100,
        },
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies[:35], total_results=len(movies), total_pages=1)
    _cache_set("animation", result, 86_400)  # 24h
    return result


def get_top10_today() -> MovieSearchResponse:
    cached = _cache_get("top10_today")
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/trending/movie/day",
        params={"api_key": settings.TMDB_API_KEY, "language": "pt-BR", "region": "BR"},
    )
    resp.raise_for_status()
    results = resp.json()["results"][:10]
    result = MovieSearchResponse(results=results, total_results=len(results), total_pages=1)
    _cache_set("top10_today", result, 3_600)  # 1h
    return result


def get_movies_by_provider(
    provider_id: int,
    page: int = 1,
    with_genres: Optional[int] = None,
) -> MovieSearchResponse:
    key = f"by_provider:{provider_id}:{page}:{with_genres}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    params: dict = {
        "api_key": settings.TMDB_API_KEY,
        "language": "pt-BR",
        "watch_region": "BR",
        "with_watch_providers": provider_id,
        "sort_by": "popularity.desc",
        "page": page,
    }
    if with_genres is not None:
        params["with_genres"] = with_genres
    resp = _http.get(f"{BASE_URL}/discover/movie", params=params)
    resp.raise_for_status()
    data = resp.json()
    result = MovieSearchResponse(
        results=data["results"],
        total_results=data["total_results"],
        total_pages=data["total_pages"],
    )
    _cache_set(key, result, 7_200)  # 2h
    return result


def get_trending_people() -> list[TrendingPersonResult]:
    cached = _cache_get("trending_people")
    if cached is not None:
        return cached

    def _fetch_day() -> list[dict]:
        resp = _http.get(
            f"{BASE_URL}/trending/person/day",
            params={"api_key": settings.TMDB_API_KEY, "language": "pt-BR"},
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def _fetch_week() -> list[dict]:
        resp = _http.get(
            f"{BASE_URL}/trending/person/week",
            params={"api_key": settings.TMDB_API_KEY, "language": "pt-BR"},
        )
        resp.raise_for_status()
        return resp.json()["results"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_day = pool.submit(_fetch_day)
        fut_week = pool.submit(_fetch_week)
        day_results = fut_day.result()
        week_results = fut_week.result()

    week_rank = {p["id"]: i for i, p in enumerate(week_results)}

    people: list[TrendingPersonResult] = []
    for day_rank, person in enumerate(day_results[:20]):
        pid = person["id"]
        if pid not in week_rank:
            direction = "new"
        elif day_rank < week_rank[pid]:
            direction = "up"
        elif day_rank == week_rank[pid]:
            direction = "stable"
        else:
            direction = "down"

        people.append(TrendingPersonResult(
            id=pid,
            name=person["name"],
            profile_path=person.get("profile_path"),
            known_for_department=person.get("known_for_department") or "Acting",
            trending_direction=direction,
        ))

    _cache_set("trending_people", people, 3_600)  # 1h
    return people


def get_national_films() -> MovieSearchResponse:
    cached = _cache_get("national_films")
    if cached is not None:
        return cached
    movies = _fetch_pages(
        f"{BASE_URL}/discover/movie",
        {
            "api_key": settings.TMDB_API_KEY,
            "language": "pt-BR",
            "with_origin_country": "BR",
            "sort_by": "popularity.desc",
            "vote_count.gte": 10,
        },
        range(1, 3),
    )
    result = MovieSearchResponse(results=movies[:35], total_results=len(movies), total_pages=1)
    _cache_set("national_films", result, 43_200)  # 12h
    return result


def get_movies_by_ids(tmdb_ids: list[int]) -> list[MovieResult]:
    def _fetch_one(movie_id: int) -> MovieResult | None:
        try:
            return get_movie(movie_id)
        except Exception:
            return None

    if not tmdb_ids:
        return []

    with ThreadPoolExecutor(max_workers=min(len(tmdb_ids), 10)) as pool:
        results = list(pool.map(_fetch_one, tmdb_ids))

    ordered = []
    for movie_id, result in zip(tmdb_ids, results):
        if result is not None:
            ordered.append(result)
    return ordered


def get_available_providers() -> list[dict]:
    cached = _cache_get("available_providers")
    if cached is not None:
        return cached
    resp = _http.get(
        f"{BASE_URL}/watch/providers/movie",
        params={"api_key": settings.TMDB_API_KEY, "language": "pt-br", "watch_region": "BR"},
    )
    resp.raise_for_status()
    allowed = {8, 119, 337, 1899, 531, 350, 307}
    result = [p for p in resp.json()["results"] if p["provider_id"] in allowed]
    _cache_set("available_providers", result, 86_400)  # 24h
    return result
