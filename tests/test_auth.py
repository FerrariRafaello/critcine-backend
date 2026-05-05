# _ IMPORTS
import time

from fastapi import status
from jose import jwt

from app.auth.security import SECRET_KEY, ALGORITHM

payload={
        "name": "Isabella",
        "age": 21,
        "cpf": "18027797799",
        "email": "isa@gmail.com",
        "password": "senha123"
    }


def test_login_success(client_auth):
    client_auth.post("/v1/users",json=payload)

    resp=client_auth.post("/v1/auth/login", data={
        "username":"isa@gmail.com",
        "password":"senha123"
    })
    assert resp.status_code==status.HTTP_200_OK
    body=resp.json()
    assert "access_token" in body
    assert body["token_type"]=="bearer"


def test_login_wrong_password(client_auth):
    client_auth.post("/v1/users", json=payload)

    resp=client_auth.post("/v1/auth/login", data={
        "username":"isa@gmail.com",
        "password":"wrong"
    })
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED


def test_login_user_not_found(client_auth):
    resp=client_auth.post("/v1/auth/login", data={
        "username":"wrong@gmail.com",
        "password":"senha123"
    })
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED


def test_protect_route_without_token(client_movie):
    resp=client_movie.post(
        "/v1/movies",
        json={
            "name":"Inception",
            "year":2010,
            "rating":9.0
        }
    )
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED


def test_protected_route_with_invalid_token(client_movie):
    resp=client_movie.post(
        "/v1/movies",
        json={"name": "Inception", "year":2010, "rating":9.0},
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert resp.status_code==status.HTTP_401_UNAUTHORIZED


def test_protected_route_with_valid_token(client_movie, auth_token):
    resp=client_movie.post(
        "/v1/movies",
        json={"name":"Inception", "year":2010, "rating":9.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code==status.HTTP_201_CREATED


def test_expired_token(client_movie):
    expired_token=jwt.encode(
        {
            "sub":"1",
            "exp":int(time.time())-60,
            "iat":int(time.time())-3660,
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    resp=client_movie.get(
        "/v1/movies",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert resp.status_code==401


def test_token_wrong_secret(client_movie):
    token=jwt.encode(
        {
            "sub":"1",
            "exp":int(time.time())+3660,
            "iat":int(time.time()),
        },
        "wrong key",
        algorithm="HS256"
    )
    resp=client_movie.get(
        "/v1/movies",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code==401


def test_token_missing_sub(client_movie):
    token=jwt.encode(
        {
            "exp":int(time.time())+3660,
            "iat":int(time.time()),
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    resp=client_movie.get(
        "/v1/movies",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code==401
