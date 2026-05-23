# _ IMPORTS
import re
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
from app.follows.database import FollowDB

# Routers
from app.movies.router import router as router_movies
from app.users.router import router as router_users
from app.auth.router import router as router_auth
from app.tmdb.router import router as router_tmdb
from app.reviews.router import router as router_reviews
from app.watchlist.router import router as router_watchlist
from app.follows.router import router as router_follows

# Security
from starlette.middleware.base import BaseHTTPMiddleware


# _ LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    # open all connection pools once at startup so every request reuses them
    app.state.db_movies = MovieDB()
    app.state.db_users = UserDB()
    app.state.db_reviews = ReviewDB()
    app.state.db_watchlist = WatchlistDB()
    app.state.db_follows = FollowDB()
    try:
        yield
    finally:
        # close pools gracefully so in-flight queries can finish
        app.state.db_movies.close_db_movies()
        app.state.db_users.close_db_users()
        app.state.db_reviews.close_db_reviews()
        app.state.db_watchlist.close_db_watchlist()
        app.state.db_follows.close_db_follows()


limiter = Limiter(key_func=get_remote_address)


# _ Main
app = FastAPI(
    title="Critcine API",
    version="2.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  #type: ignore

# Loguru config
logger.remove()
logger.add(sys.stdout, level="INFO", serialize=True)


# only allow requests from our own frontend origins
origins = [
    "http://localhost:3000",
    "https://critcine-production-95d5.up.railway.app",
    "https://critcine.com",
    "https://www.critcine.com",
    "https://critcine-frontend-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


# _ Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # tell browsers not to sniff content types or allow framing
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # 2-year HSTS so browsers remember to use HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


# _ Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # attach a unique ID to every request so errors can be correlated in logs
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# _ Payload Size Middleware (1MB)
@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    # reject huge uploads early — we never need anything larger than 1 MB
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
# paths that only scanners and bots ever request — log and return 404
_HONEYPOT_PATHS = {
    "/admin", "/wp-login.php", "/wp-admin", "/.env",
    "/phpMyAdmin", "/manager", "/.git/config", "/config.php",
    "/backup", "/shell.php", "/api/v1/admin", "/console",
    "/actuator", "/actuator/env", "/actuator/health",
    "/api/v1/env", "/.DS_Store", "/server-status",
    "/telescope", "/horizon", "/laravel", "/login",
    "/.well-known/security.txt",
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
app.include_router(router_follows)


# _ Health Check
@app.get("/health")
def healthcheck():
    return {"status": "ok"}


_PYDANTIC_TO_PT: dict[str, str] = {
        "Field required": "Campo obrigatório",
        "value is not a valid email address": "E-mail inválido",
        "String should have at least 2 characters": "Mínimo de 2 caracteres",
        "String should have at most 50 characters": "Máximo de 50 caracteres",
        "String should have at least 8 characters": "Mínimo de 8 caracteres",
        "String should have at most 128 characters": "Máximo de 128 caracteres",
        "Input should be a valid integer": "Deve ser um número inteiro",
        "Input should be greater than or equal to 16": "Idade mínima: 16 anos",
        "Input should be less than or equal to 100": "Idade máxima: 100 anos",
        "Password must contain at least one uppercase letter": "Senha precisa ter ao menos uma letra maiúscula",
        "Password must contain at least one lowercase letter": "Senha precisa ter ao menos uma letra minúscula",
        "Password must contain at least one digit": "Senha precisa ter ao menos um número",
        "CPF inválido": "CPF inválido",
    }


def _translate_pydantic(msg: str)-> str:
    clean = re.sub(r"^Value error, ", "", msg)
    return _PYDANTIC_TO_PT.get(clean, clean)


# _ Handler Validation Error
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    fields: dict[str,str] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = next((str(p) for p in reversed(loc) if not isinstance(p, int)), "body")
        
        if field not in fields:
            fields[field] = _translate_pydantic(error.get("msg", "Valor inválido"))

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Verifique os campos e tente novamente.",
                "path": request.url.path,
                "fields": fields,
            }
        }
    )


# _ Fallback
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    # include request_id so we can find the full traceback in logs
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
