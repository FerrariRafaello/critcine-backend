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
def test_crud_flow_users(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Get the authenticated user's own ID
    me_resp = client_users.get("/v1/users/me", headers=headers)
    assert me_resp.status_code == status.HTTP_200_OK
    user_id = me_resp.json()["id"]

    # List
    resp = client_users.get("/v1/users", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) >= 1

    # Get
    resp = client_users.get(f"/v1/users/{user_id}", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["id"] == user_id

    # Update own user
    updated_json = {
        "name": "rafaello",
        "age": 22,
        "cpf": "52998224725",
        "email": "rafa@gmail.com"
    }
    resp = client_users.put(
        f"/v1/users/{user_id}",
        json=updated_json,
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    updated = resp.json()
    assert updated["name"] == updated_json["name"]
    assert updated["cpf"] == updated_json["cpf"]
    assert "id" in updated

    # Patch bio, avatar, cover
    resp = client_users.patch(
        f"/v1/users/{user_id}",
        json={
            "bio": "I love movies!",
            "avatar_id": "cat",
            "cover_id": "sunset",
            "pronouns": "he/him",
            "favorite_genres": "Action, Drama, Comedy"
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    patched = resp.json()
    assert patched["bio"] == "I love movies!"
    assert patched["avatar_id"] == "cat"
    assert patched["cover_id"] == "sunset"
    assert patched["pronouns"] == "he/him"
    assert patched["favorite_genres"] == "Action, Drama, Comedy"
    assert patched["id"] == user_id

    # Patch age - bio should persist
    resp = client_users.patch(
        f"/v1/users/{user_id}",
        json={"age": 25},
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    patched = resp.json()
    assert patched["age"] == 25
    assert patched["bio"] == "I love movies!"
    assert patched["pronouns"] == "he/him"
    assert patched["favorite_genres"] == "Action, Drama, Comedy"
    assert patched["id"] == user_id

    # Delete own user
    resp = client_users.delete(f"/v1/users/{user_id}", headers=headers)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


# __ NOT FOUND CASES
# With ownership check, any user_id != current user returns 403 before 404
def test_get_not_found(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_users.get("/v1/users/9999", headers=headers)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_not_found(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_users.put(
        "/v1/users/9999",
        json={
            "name": "Isabella",
            "age": 21,
            "cpf": "18027797799",
            "email": "isa@gmail.com"
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_patch_not_found(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_users.patch(
        "/v1/users/9999",
        json={"name": "Isabella"},
        headers=headers,
    )
    assert_error_contract(resp, 403, "forbidden", "/v1/users/9999")


def test_delete_not_found(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client_users.delete("/v1/users/9999", headers=headers)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_create_duplicate_cpf_conflict(client_users):
    payload1 = {
        "name": "Ana",
        "age": 25,
        "cpf": "18027797799",
        "email": "ana1@gmail.com",
        "password": "Senha123"
    }
    payload2 = {
        "name": "Bia",
        "age": 26,
        "cpf": "18027797799",
        "email": "bia2@gmail.com",
        "password": "Senha123"
    }
    resp1 = client_users.post("/v1/users", json=payload1)
    assert resp1.status_code == 201

    resp2 = client_users.post("/v1/users", json=payload2)
    assert_error_contract(resp2, 409, "conflict", "/v1/users")


def test_cpf_raise_error(client_users, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Patch the authenticated user's own profile with an invalid CPF
    me_resp = client_users.get("/v1/users/me", headers=headers)
    assert me_resp.status_code == status.HTTP_200_OK
    user_id = me_resp.json()["id"]

    resp = client_users.patch(
        f"/v1/users/{user_id}",
        json={"cpf": "99999999999"},
        headers=headers,
    )
    assert_error_contract(resp, 422, "validation_error", f"/v1/users/{user_id}")
    body = resp.json()
    assert "fields" in body["error"]
    assert "cpf" in body["error"]["fields"]