# _ IMPORTS
import os
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.schemas import TokenOut
from app.auth.service import AuthService


limit = lambda: "1000/minute" if os.getenv("TESTING") else "5/minute"
router=APIRouter(prefix="/v1/auth", tags=["Auth"])
limiter=Limiter(key_func=get_remote_address)

def get_auth_service(request:Request)->AuthService:
    return AuthService(request.app.state.db_users)


@router.post("/login", response_model=TokenOut)
@limiter.limit(limit)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm=Depends(),
    service:AuthService=Depends(get_auth_service)
):
    return service.login(form.username, form.password)
