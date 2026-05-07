# _ IMPORTS
from fastapi import status


def test_create_review(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    resp=client_auth.post("/v1/reviews", json={
        "tmdb_movie_id":550,
        "rating":8.5,
        "comment":"Great movie!"
    }, headers=headers)
    assert resp.status_code==status.HTTP_201_CREATED
    body=resp.json()
    assert body["tmdb_movie_id"]==550
    assert body["rating"]==8.5
    assert "id" in body


def test_client_duplicate_review(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    client_auth.post("/v1/reviews", json={
        "tmdb_movie_id":551,
        "rating":8.5,
    }, headers=headers)
    resp = client_auth.post("/v1/reviews", json={
        "tmdb_movie_id":551,
        "rating":8.5,
    }, headers=headers)
    assert resp.status_code==status.HTTP_409_CONFLICT


def test_get_reviews_by_movie(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 552,
        "rating": 8.5
    }, headers=headers)
    resp=client_auth.get("/v1/reviews/movie/552", headers=headers)
    assert resp.status_code==status.HTTP_200_OK
    assert len(resp.json()) >= 1


def test_update_review(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    created=client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 553,
        "rating": 8.5
    }, headers=headers).json()
    resp=client_auth.patch(
        f"/v1/reviews/{created['id']}",
        json={"rating": 9.0},
        headers=headers
    )
    assert resp.status_code==status.HTTP_200_OK
    assert resp.json()["rating"]==9.0


def test_delete_review(client_auth, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    created=client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 554,
        "rating": 8.5
    }, headers=headers).json()
    resp=client_auth.delete(
        f"/v1/reviews/{created['id']}",
        headers=headers
    )
    assert resp.status_code==status.HTTP_204_NO_CONTENT


def test_create_review_without_token(client_auth):
    resp=client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 550,
        "rating": 8.5
    })
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED
