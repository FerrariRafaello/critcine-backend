# _ IMPORTS
import os
os.environ["TESTING"]="true"

import pytest
import sys

from fastapi.testclient import TestClient
from pathlib import Path

from dotenv import load_dotenv

# _ Main Router
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(str(ROOT_DIR/".env"))

# DBs
from app.core.database_movies import MovieDB
from app.core.database_users import UserDB
from app.reviews.database import ReviewDB

# Services
from app.movies.service import MovieService
from app.users.service import UserService

# Routers
from app.movies.router import get_movie_service
from app.users.router import get_user_service
from app.reviews.router import get_review_service

# Auth
from app.auth.router import get_auth_service
from app.auth.service import AuthService
from app.reviews.service import ReviewService

# Pool
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

# Main
from app.main import app


# _ Fixtures (Movies/Users)
@pytest.fixture(scope="function")
def test_db_movies():
    db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not configured"

    with ConnectionPool(
        db_url,
        min_size=2,
        max_size=10,
        open=True,
        kwargs={"row_factory": dict_row}
    ) as pool:
        with pool.connection() as conn:
            conn.execute("TRUNCATE TABLE movies RESTART IDENTITY;")
        yield MovieDB(pool=pool)#type: ignore


# _ Reviews
@pytest.fixture(scope="function")
def test_db_reviews():
    db_url=os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not configured"

    with ConnectionPool(
        db_url,
        min_size=2,
        max_size=10,
        open=True,
        kwargs={"row_factory": dict_row}
    ) as pool:
        with pool.connection() as conn:
            conn.execute("TRUNCATE TABLE reviews RESTART IDENTITY;")
        yield ReviewDB(pool=pool) #type: ignore


@pytest.fixture(scope="function")
def test_db_users():
    db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not configured"

    with ConnectionPool(
        db_url,
        min_size=2,
        max_size=10,
        open=True,
        kwargs={"row_factory": dict_row}
    ) as pool:
        with pool.connection() as conn:
            conn.execute("TRUNCATE TABLE reviews, users RESTART IDENTITY CASCADE;")
        yield UserDB(pool=pool)#type: ignore


@pytest.fixture(scope="function")
def client_movie(test_db_movies):
    def override_service():
        return MovieService(test_db_movies)

    app.dependency_overrides[get_movie_service]=override_service

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_users(test_db_users):
    def override_service():
        return UserService(test_db_users)

    app.dependency_overrides[get_user_service]=override_service

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_auth(test_db_users, test_db_reviews):
    def override_auth():
        return AuthService(test_db_users)

    def override_user_service():
        return UserService(test_db_users)

    def override_review_service():
        return ReviewService(test_db_reviews)

    app.dependency_overrides[get_auth_service]=override_auth
    app.dependency_overrides[get_user_service]=override_user_service
    app.dependency_overrides[get_review_service]=override_review_service

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_token(client_auth):
    client_auth.post("/v1/users", json={
        "name": "Test User",
        "age": 25,
        "cpf": "52998224725",
        "email": "token@gmail.com",
        "password": "secret123"
    })

    resp=client_auth.post("/v1/auth/login", data={
        "username": "token@gmail.com",
        "password": "secret123"
    })

    assert resp.status_code==200, (
        f"auth_token fixture: login failed with {resp.status_code} - {resp.json()}"
    )

    token=resp.json().get("access_token")
    assert token, "auth_token fixture: response has no acess_token"

    return token
