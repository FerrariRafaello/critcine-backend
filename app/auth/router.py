# _ IMPORTS
import os
from fastapi import APIRouter, Depends, Request, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.schemas import TokenOut
from app.auth.service import AuthService
from app.core.brute_force import check_brute_force, record_failure, record_success


router = APIRouter(prefix="/v1/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


def get_limit() -> str:
    return "1000/minute" if os.getenv("TESTING") else "5/minute"

def get_auth_service(request: Request) -> AuthService:
    return AuthService(request.app.state.db_users)


@router.post("/login", response_model=TokenOut)
@limiter.limit(get_limit)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    ip = get_remote_address(request)

    blocked, remaining = check_brute_force(ip)
    if blocked:
        logger.warning("brute_force_blocked ip={} remaining_seconds={}", ip, remaining)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts. Try again in {remaining} seconds."
        )

    try:
        result = service.login(form.username, form.password)
        record_success(ip)
        logger.info("login_success ip={}", ip)
        return result
    except HTTPException:
        locked = record_failure(ip)
        if locked:
            logger.warning("brute_force_lockout ip={} email={}", ip, form.username)
        else:
            logger.warning("login_failed ip={} email={}", ip, form.username)
        raise
