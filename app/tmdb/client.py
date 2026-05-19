# _ IMPORTS
import httpx

from typing import Optional

from app.core.config import settings
from app.tmdb.schemas import MovieResult, MovieSearchResponse


BASE_URL = "https://api.themoviedb.org/3"


def search_movies(query:str, page:int=1)->MovieSearchResponse:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/search/movie",
            params={
                "api_key":settings.TMDB_API_KEY,
                "query":query,
                "page":page,
                "language": "pt-BR"
            }
        )
        resp.raise_for_status()
        return MovieSearchResponse(**resp.json())


def get_movie(movie_id:int)->MovieResult:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={
                "api_key":settings.TMDB_API_KEY,
                "language":"pt-BR"
            }
        )
        resp.raise_for_status()
        return MovieResult(**resp.json())


def get_trending()->MovieSearchResponse:
    results=[]
    # seen_ids prevents duplicates when TMDB returns the same movie on multiple pages
    seen_ids=set()
    for page in range(1,3):
        with httpx.Client() as client:
            resp=client.get(
                f"{BASE_URL}/trending/movie/week",
                params={"api_key": settings.TMDB_API_KEY, "language": "pt-br", "page": page}
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results, total_results=len(results), total_pages=1)


def get_now_playing()->MovieSearchResponse:
    results=[]
    seen_ids=set()
    for page in range(1,3):
        with httpx.Client() as client:
            resp =client.get(
                f"{BASE_URL}/movie/now_playing",
                params={"api_key":settings.TMDB_API_KEY, "language":"pt-br", "page":page}
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results, total_results=len(results), total_pages=1)


def get_movie_credits(movie_id:int)->dict:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/movie/{movie_id}/credits",
            params={"api_key":settings.TMDB_API_KEY, "language":"pt-br"}
        )
        resp.raise_for_status()
        return resp.json()


def get_movie_videos(movie_id:int)->dict:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/movie/{movie_id}/videos",
            params={"api_key": settings.TMDB_API_KEY, "language":"pt-br"}
        )
        resp.raise_for_status()
        return resp.json()


def get_top_rated()-> MovieSearchResponse:
    results=[]
    seen_ids=set()
    for page in range(1,3):
        with httpx.Client() as client:
            resp=client.get(
                f"{BASE_URL}/movie/top_rated",
                params={"api_key": settings.TMDB_API_KEY, "language": "pt-BR", "page": page}
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results, total_results=len(results), total_pages=1)


def get_watch_providers(movie_id: int) -> dict:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/movie/{movie_id}/watch/providers",
            params={"api_key": settings.TMDB_API_KEY}
        )
        resp.raise_for_status()
        return resp.json()


def get_external_ids(movie_id: int) -> dict:
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/movie/{movie_id}/external_ids",
            params={"api_key": settings.TMDB_API_KEY}
        )
        resp.raise_for_status()
        return resp.json()
    

def discover_movies_by_genre(
    genre_id: int,
    page: int = 1,
    sort_by: str = "release_date.desc",
) -> MovieSearchResponse:
    with httpx.Client() as client:
        resp = client.get(
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
        return MovieSearchResponse(**resp.json())


def get_for_you(genres:str)-> MovieSearchResponse:
    results=[]
    seen_ids=set()
    genres_ids = genres.replace(",", "|")
    for page in range(1,3):
        with httpx.Client() as client:
            resp=client.get(
                f"{BASE_URL}/discover/movie",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "pt-BR",
                    "with_genres": genres_ids,
                    "sort_by": "popularity.desc",
                    "vote_count.gte": 100,
                    "page": page 
                }
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results[:35], total_results=len(results), total_pages=1)


def get_classics()->MovieSearchResponse:
    results=[]
    seen_ids=set()
    for page in range(1,3):
        with httpx.Client() as client:
            resp=client.get(
                f"{BASE_URL}/discover/movie",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "pt-BR",
                    "sort_by": "vote_count.desc",
                    "primary_release_date.lte": "1990-12-31",
                    "vote_average.gte": 7.0,
                    "page": page
                }
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results[:35], total_results=len(results), total_pages=1)


def get_animation() -> MovieSearchResponse:
    results = []
    seen_ids = set()
    for page in range(1, 3):
        with httpx.Client() as client:
            resp = client.get(
                f"{BASE_URL}/discover/movie",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "pt-BR",
                    "with_genres": 16,
                    "sort_by": "popularity.desc",
                    "vote_count.gte": 100,
                    "page": page
                }
            )
            resp.raise_for_status()
            for movie in resp.json()["results"]:
                if movie["id"] not in seen_ids:
                    seen_ids.add(movie["id"])
                    results.append(movie)
    return MovieSearchResponse(results=results[:35], total_results=len(results), total_pages=1)


def get_top10_today()->MovieSearchResponse:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/trending/movie/day",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "pt-BR",
                "region": "BR"
            }
        )
        resp.raise_for_status()
        results=resp.json()["results"][:10]
        return MovieSearchResponse(results=results, total_results=len(results), total_pages=1)


def get_movies_by_provider(
    provider_id: int,
    page: int = 1,
    with_genres: Optional[int] = None
) -> MovieSearchResponse:
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "pt-BR",
        "watch_region": "BR",
        "with_watch_providers": provider_id,
        "sort_by": "popularity.desc",
        "page": page,
    }
    if with_genres is not None:
        params["with_genres"] = with_genres
    with httpx.Client() as client:
        resp = client.get(
            f"{BASE_URL}/discover/movie",
            params=params
        )
        resp.raise_for_status()
        data = resp.json()
        return MovieSearchResponse(
            results=data["results"],
            total_results=data["total_results"],
            total_pages=data["total_pages"]
        )


def get_available_providers() -> list[dict]:
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/watch/providers/movie",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "pt-br",
                "watch_region": "BR"
            }
        )
        resp.raise_for_status()
        results=resp.json()["results"]

        # only return the main streaming services available in Brazil
        allowed = {8, 119, 337, 1899, 531, 350, 307}
        return [p for p in results if p["provider_id"] in allowed]
