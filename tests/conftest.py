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
from app.watchlist.database import WatchlistDB
from app.follows.database import FollowDB

# Services
from app.movies.service import MovieService
from app.users.service import UserService
from app.watchlist.service import WatchlistService

# Routers
from app.movies.router import get_movie_service
from app.users.router import get_user_service, get_follow_db
from app.reviews.router import get_review_service
from app.watchlist.router import get_watchlist_service
from app.follows.router import get_follow_service

# Auth
from app.auth.router import get_auth_service
from app.auth.service import AuthService
from app.reviews.service import ReviewService
from app.follows.service import FollowService

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
            try:
                conn.execute("TRUNCATE TABLE review_likes, reviews RESTART IDENTITY CASCADE;")
            except Exception as e:
                if "does not exist" not in str(e):
                    raise
        yield ReviewDB(pool=pool) #type: ignore



@pytest.fixture(scope="function")
def test_db_watchlist():
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
            conn.execute("TRUNCATE TABLE watchlist RESTART IDENTITY")
        yield WatchlistDB(pool=pool) #type: ignore


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
            conn.execute("TRUNCATE TABLE follows, reviews, users RESTART IDENTITY CASCADE;")
        yield UserDB(pool=pool)#type: ignore


@pytest.fixture(scope="function")
def test_db_follows(test_db_users):
    db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not configured"

    with ConnectionPool(
        db_url,
        min_size=2,
        max_size=10,
        open=True,
        kwargs={"row_factory": dict_row}
    ) as pool:
        yield FollowDB(pool=pool)  # type: ignore


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
def client_users(test_db_users, test_db_follows):
    def override_service():
        return UserService(test_db_users)

    def override_follow_db():
        return test_db_follows

    def override_follow_service():
        return FollowService(test_db_follows)

    app.dependency_overrides[get_user_service] = override_service
    app.dependency_overrides[get_follow_db] = override_follow_db
    app.dependency_overrides[get_follow_service] = override_follow_service

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_auth(test_db_users, test_db_reviews, test_db_watchlist, test_db_follows):
    def override_auth():
        return AuthService(test_db_users)

    def override_user_service():
        return UserService(test_db_users)

    def override_review_service():
        return ReviewService(test_db_reviews)

    def override_watchlist_service():
        return WatchlistService(test_db_watchlist)

    def override_follow_db():
        return test_db_follows

    def override_follow_service():
        return FollowService(test_db_follows)

    app.dependency_overrides[get_auth_service] = override_auth
    app.dependency_overrides[get_user_service] = override_user_service
    app.dependency_overrides[get_review_service] = override_review_service
    app.dependency_overrides[get_watchlist_service] = override_watchlist_service
    app.dependency_overrides[get_follow_db] = override_follow_db
    app.dependency_overrides[get_follow_service] = override_follow_service

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
        "password": "Secret123"
    })

    resp=client_auth.post("/v1/auth/login", data={
        "username": "token@gmail.com",
        "password": "Secret123"
    })

    assert resp.status_code==200, (
        f"auth_token fixture: login failed with {resp.status_code} - {resp.json()}"
    )

    token=resp.json().get("access_token")
    assert token, "auth_token fixture: response has no access_token"

    return token
