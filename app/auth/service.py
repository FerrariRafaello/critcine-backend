from app.core.database_users import UserDB
from fastapi import HTTPException, status
from app.auth.schemas import TokenOut
from app.auth.security import verify_password, create_access_token


class AuthService:
    def __init__(self, db: UserDB) -> None:
        self.db = db

    def login(self, email: str, password: str) -> TokenOut:
        user = self.db.get_user_by_email(email)
        if user is None or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        # bumping token_version invalidates any previously issued tokens for this user
        new_version = self.db.increment_token_version(user["id"])
        token = create_access_token(user["id"], version=new_version)
        return TokenOut(access_token=token)
