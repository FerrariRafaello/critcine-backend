# _ IMPORTS
from fastapi import status


def test_add_to_watchlist(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    resp=client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":550,
        "status":"want_to_watch"
    }, headers=headers)
    assert resp.status_code==status.HTTP_201_CREATED
    body=resp.json()
    assert body["tmdb_movie_id"]==550
    assert body["status"]=="want_to_watch"
    assert "id" in body


def test_add_duplicate_to_watchlist(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":551,
        "status":"want_to_watch"
    }, headers=headers)
    resp=client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":551,
        "status":"want_to_watch"
    }, headers=headers)
    assert resp.status_code==status.HTTP_409_CONFLICT


def test_get_watchlist(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":552,
        "status":"want_to_watch"
    }, headers=headers)
    resp=client_auth.get("/v1/watchlist", headers=headers)
    assert resp.status_code==status.HTTP_200_OK
    assert len(resp.json()) >= 1


def test_update_watchlist_item(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    created=client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":553,
        "status":"want_to_watch"
    }, headers=headers).json()
    resp=client_auth.patch(
        f"/v1/watchlist/{created['id']}",
        json={"status": "watched"},
        headers=headers
    )
    assert resp.status_code==status.HTTP_200_OK
    assert resp.json()["status"]=="watched"


def test_delete_watchlist_item(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    created=client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":554,
        "status":"want_to_watch"
    }, headers=headers).json()
    resp=client_auth.delete(
        f"/v1/watchlist/{created['id']}",
        headers=headers
    )
    assert resp.status_code==status.HTTP_204_NO_CONTENT


def test_add_to_watchist_without_token(client_auth):
    resp=client_auth.post("/v1/watchlist", json={
        "tmdb_movie_id":550,
        "status":"want_to_watch"
    })
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED
