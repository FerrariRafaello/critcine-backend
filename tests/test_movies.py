# __ IMPORTS
from fastapi import status


# __ Helper
def assert_error_contract(
        resp,
        expected_status,
        expected_code,
        expected_path):
    assert resp.status_code == expected_status
    body=resp.json()
    error = body["error"]
    assert error["code"] == expected_code
    assert error["path"] == expected_path
    assert isinstance(error["message"], str)
    assert error["message"] != ""


# __ CRUD Flow
def test_crud_flow_movies(client_movie, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload={
        "name": "La La Land",
        "year": 2019,
        "rating": 9.0
    }

    # Create
    resp = client_movie.post(
        "/v1/movies",
        json=payload,
        headers=headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    created = resp.json()
    movie_id = created["id"]
    assert created["name"] == payload["name"]
    assert "id" in created

    # List
    resp = client_movie.get(
        "/v1/movies",
        headers=headers
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) >= 1

    # Get
    resp = client_movie.get(
        f"/v1/movies/{movie_id}",
        headers=headers
    )
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["id"] ==  movie_id

    # Update
    updated_json = {
        "name": "Enrolados",
        "year": 2016,
        "rating": 7.7
    }

    resp = client_movie.put(
        f"/v1/movies/{movie_id}",
        json=updated_json,
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK

    updated = resp.json()
    movie_id = updated["id"]
    assert updated["name"] == updated_json["name"]
    assert updated["rating"] == updated_json["rating"]
    assert "id" in updated

    # Patch
    resp = client_movie.patch(
        f"/v1/movies/{movie_id}",
        json={
            "year": 2015
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK

    patched = resp.json()
    assert patched["id"] == movie_id
    assert patched["year"] == 2015

    # Delete
    resp = client_movie.delete(
        f"/v1/movies/{movie_id}",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT


# __ NOT FOUND
def test_get_not_found(client_movie, auth_token):
    headers={"Authorization": f"Bearer {auth_token}"}
    resp = client_movie.get("/v1/movies/9999", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_not_found(client_movie, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_movie.put(
        "/v1/movies/9999",
        json={
            "name": "oi",
            "year": 2000,
            "rating": 1.
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_patch_not_found(client_movie, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_movie.patch(
        "/v1/movies/9999",
        json={
            "name": "Hello"
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_not_found(client_movie, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_movie.delete("/v1/movies/9999", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
