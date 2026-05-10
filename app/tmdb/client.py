# _ IMPORTS
import httpx
from app.core.config import settings
from app.tmdb.schemas import MovieResult, MovieSearchResponse


BASE_URL="https://api.themoviedb.org/3"


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
    with httpx.Client() as client:
        resp=client.get(
            f"{BASE_URL}/trending/movie/week",
            params={"api_key": settings.TMDB_API_KEY, "language": "pt-br"}
        )
        resp.raise_for_status()
        return MovieSearchResponse(**resp.json())


def get_now_playing()->MovieSearchResponse:
    with httpx.Client() as client:
        resp =client.get(
            f"{BASE_URL}/movie/now_playing",
            params={"api_key":settings.TMDB_API_KEY, "language":"pt-br"}
        )
        resp.raise_for_status()
        return MovieSearchResponse(**resp.json())
