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


def test_like_own_review(client_auth, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    review = client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 560,
        "rating": 7.0
    }, headers=headers).json()
    resp = client_auth.post(f"/v1/reviews/{review['id']}/like", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["likes"] == 1


def test_like_review_already_liked(client_auth, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    review = client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 561,
        "rating": 7.0
    }, headers=headers).json()
    client_auth.post(f"/v1/reviews/{review['id']}/like", headers=headers)
    resp = client_auth.post(f"/v1/reviews/{review['id']}/like", headers=headers)
    assert resp.status_code == status.HTTP_409_CONFLICT


def test_unlike_review(client_auth, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    review = client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 562,
        "rating": 7.0
    }, headers=headers).json()
    client_auth.post(f"/v1/reviews/{review['id']}/like", headers=headers)
    resp = client_auth.delete(f"/v1/reviews/{review['id']}/like", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["likes"] == 0


def test_like_review_from_another_user(client_auth, auth_token):
    # user1 cria review
    headers1 = {"Authorization": f"Bearer {auth_token}"}
    review = client_auth.post("/v1/reviews", json={
        "tmdb_movie_id": 563,
        "rating": 8.0
    }, headers=headers1).json()

    # user2 se registra e faz login
    client_auth.post("/v1/users", json={
        "name": "Other User",
        "age": 22,
        "cpf": "11144477735",
        "email": "other@gmail.com",
        "password": "Secret123"
    })
    token2 = client_auth.post("/v1/auth/login", data={
        "username": "other@gmail.com",
        "password": "Secret123"
    }).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp = client_auth.post(f"/v1/reviews/{review['id']}/like", headers=headers2)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["likes"] == 1
