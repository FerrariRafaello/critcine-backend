# _ IMPORTS
import respx
import httpx

from fastapi import status


@respx.mock
def test_search_movies(client_auth, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    respx.get("https://api.themoviedb.org/3/search/movie").mock(
        return_value=httpx.Response(200, json={
            "results": [
                {
                    "id": 1,
                    "title": "Inception",
                    "overview": "A mind-bending thriller",
                    "release_date": "2010-07-16",
                    "poster_path": "/poster.jpg",
                    "vote_average": 8.8
                }
            ],
            "total_results": 1,
            "total_pages": 1
        })
    )

    resp = client_auth.get(
        "/v1/tmdb/search",
        params={"q": "Inception"},
        headers=headers
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["total_results"] == 1
    assert body["results"][0]["title"] == "Inception"


@respx.mock
def test_get_movie_detail(client_auth, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    respx.get("https://api.themoviedb.org/3/movie/1").mock(
        return_value=httpx.Response(200, json={
            "id": 1,
            "title": "Inception",
            "overview": "A mind-bending thriller",
            "release_date": "2010-07-16",
            "poster_path": "/poster.jpg",
            "vote_average": 8.8
        })
    )

    resp = client_auth.get(
        "/v1/tmdb/movies/1",
        headers=headers
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["title"] == "Inception"


@respx.mock
def test_search_without_token(client_auth):
    resp = client_auth.get("/v1/tmdb/search", params={"q": "Inception"})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
