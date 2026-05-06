# _ IMPORTS
import jwt as pyjwt

from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
# from jose import JWTError, jwt

from app.core.config import settings


SECRET_KEY:str=settings.JWT_SECRET
ALGORITHM:str=settings.JWT_ALGORITHM
EXPIRE_MIN:int=settings.JWT_EXPIRE_MINUTES

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET is no configured")
assert isinstance(SECRET_KEY, str)

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

def hash_password(password:str)->str:
    return pwd_context.hash(password)


def verify_password(plain:str, hashed:str)->bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id:int)->str:
    expire=datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    return pyjwt.encode(
        {"sub": str(user_id), "exp":expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user_id(token:str=Depends(oauth2_scheme))->int:
    try:
        payload=pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id=payload.get("sub")
        if user_id is None:
            raise ValueError
        return int(user_id)
    except (PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
