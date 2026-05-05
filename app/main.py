# _ IMPORTS
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager

# DBs
from app.core.database_movies import MovieDB
from app.core.database_users import UserDB

# Routers
from app.movies.router import router as router_movies
from app.users.router import router as router_users
from app.auth.router import router as router_auth


# _ LIFESPAN
@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.db_movies=MovieDB()
    app.state.db_users=UserDB()
    try:
        yield
    finally:
        app.state.db_movies.close_db_movies()
        app.state.db_users.close_db_users()


# _ Main
app=FastAPI(
    title="Users/Movies API",
    version="2.0.0",
    lifespan=lifespan
)

# _ Helper
def build_error(code:str, message:str, path:str):
    return {"error": {"code":code, "message":message, "path":path}}


# _ Including Routes
app.include_router(router_movies)
app.include_router(router_users)
app.include_router(router_auth)


# _ Health Check
@app.get(
    "/health"
)
def healthcheck():
    return {"status":"ok"}


# _ Handler HTTPException
@app.exception_handler(HTTPException)
async def http_error_handler(request:Request, exc: HTTPException):
    code="http_error"
    message=str(exc.detail)

    if exc.status_code == 404:
        code="not_found"
    elif exc.status_code == 409:
        code="conflict"
    elif exc.status_code == 422:
        code="validation_error"

    return JSONResponse(
        status_code=exc.status_code,
        content=build_error(
            code,
            message,
            request.url.path
        ),
    )


# _ Handler Validation Error
@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
):
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
async def unhandled_error_handler(
    request:Request,
    exc:Exception
):
    return JSONResponse(
        status_code=500,
        content=build_error("internal_error", "internal server error", request.url.path)
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
