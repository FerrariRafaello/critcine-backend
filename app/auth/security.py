# _ IMPORTS
import os
import jwt as pyjwt

from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings


SECRET_KEY: str = settings.JWT_SECRET
ALGORITHM: str = settings.JWT_ALGORITHM
EXPIRE_MIN: int = settings.JWT_EXPIRE_MINUTES

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET is not configured")
assert isinstance(SECRET_KEY, str)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, version: int = 0) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    return pyjwt.encode(
        {"sub": str(user_id), "exp": expire, "ver": version},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    request: Request = None  # type: ignore[assignment]
) -> int:
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        token_ver = int(payload.get("ver", 0))
        if user_id_str is None:
            raise ValueError
        user_id = int(user_id_str)
    except (PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Valida versão do token contra o banco — garante sessão única por usuário.
    # Pulado em testes (usuários vivem em DB separado do app.state.db_users).
    if not os.getenv("TESTING") and request is not None:
        db = request.app.state.db_users
        current_ver = db.get_token_version(user_id)
        if current_ver is None or token_ver != current_ver:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session invalidated. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return user_id
