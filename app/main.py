# _ IMPORTS
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

# Logging
from loguru import logger
import sys

from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# DBs
from app.core.database_movies import MovieDB
from app.core.database_users import UserDB
from app.reviews.database import ReviewDB
from app.watchlist.database import WatchlistDB

# Routers
from app.movies.router import router as router_movies
from app.users.router import router as router_users
from app.auth.router import router as router_auth
from app.tmdb.router import router as router_tmdb
from app.reviews.router import router as router_reviews
from app.watchlist.router import router as router_watchlist

# Security
from starlette.middleware.base import BaseHTTPMiddleware


# _ LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_movies = MovieDB()
    app.state.db_users = UserDB()
    app.state.db_reviews = ReviewDB()
    app.state.db_watchlist = WatchlistDB()
    try:
        yield
    finally:
        app.state.db_movies.close_db_movies()
        app.state.db_users.close_db_users()
        app.state.db_reviews.close_db_reviews()
        app.state.db_watchlist.close_db_watchlist()


limiter = Limiter(key_func=get_remote_address)


# _ Main
app = FastAPI(
    title="Cinelog API",
    version="2.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Loguru config
logger.remove()
logger.add(sys.stdout, level="INFO", serialize=True)


origins = [
    "http://localhost:3000",
    "https://cinelog-production-95d5.up.railway.app",
    "https://cinelog-frontend-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# _ Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


# _ Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# _ Payload Size Middleware (1MB)
@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_000_000:
        ip = request.client.host if request.client else "unknown"
        logger.warning("payload_too_large bytes={} path={} ip={}", content_length, request.url.path, ip)
        return JSONResponse(
            status_code=413,
            content=build_error("payload_too_large", "Request body too large", request.url.path)
        )
    return await call_next(request)


# _ Honeypot Middleware
_HONEYPOT_PATHS = {
    "/admin", "/wp-login.php", "/wp-admin", "/.env",
    "/phpMyAdmin", "/manager", "/.git/config", "/config.php",
    "/backup", "/shell.php", "/api/v1/admin", "/console",
}

@app.middleware("http")
async def honeypot(request: Request, call_next):
    if request.url.path in _HONEYPOT_PATHS:
        ip = request.client.host if request.client else "unknown"
        logger.warning(
            "honeypot_triggered path={} method={} ip={} user_agent={}",
            request.url.path,
            request.method,
            ip,
            request.headers.get("user-agent", "unknown")
        )
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    return await call_next(request)


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)


# _ Helper
def build_error(code: str, message: str, path: str):
    return {"error": {"code": code, "message": message, "path": path}}


# _ Including Routes
app.include_router(router_movies)
app.include_router(router_users)
app.include_router(router_auth)
app.include_router(router_tmdb)
app.include_router(router_reviews)
app.include_router(router_watchlist)


# _ Health Check
@app.get("/health")
def healthcheck():
    return {"status": "ok"}


# _ Handler HTTPException
@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    code = "http_error"
    message = str(exc.detail)

    if exc.status_code == 401:
        code = "unauthorized"
    elif exc.status_code == 403:
        code = "forbidden"
    elif exc.status_code == 404:
        code = "not_found"
    elif exc.status_code == 409:
        code = "conflict"
    elif exc.status_code == 422:
        code = "validation_error"

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error(code, message, request.url.path),
    )


# _ Handler Validation Error
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = jsonable_encoder(
        exc.errors(),
        custom_encoder={Exception: lambda e: str(e)}
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "path": request.url.path,
                "details": details
            }
        }
    )


# _ Fallback
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("unhandled_error request_id={} path={}", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content=build_error("internal_error", "Internal server error", request.url.path)
    )


@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exc: LookupError):
    return JSONResponse(
        status_code=404,
        content=build_error("not_found", str(exc), request.url.path),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=409,
        content=build_error("conflict", str(exc), request.url.path),
    )
