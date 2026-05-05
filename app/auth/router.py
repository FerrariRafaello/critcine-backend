# _ IMPORTS
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import TokenOut
from app.auth.service import AuthService


router=APIRouter(prefix="/v1/auth", tags=["Auth"])

def get_auth_service(request:Request)->AuthService:
    return AuthService(request.app.state.db_users)


@router.post("/login", response_model=TokenOut)
def login(
    form: OAuth2PasswordRequestForm=Depends(),
    service:AuthService=Depends(get_auth_service)
):
    return service.login(form.username, form.password)
