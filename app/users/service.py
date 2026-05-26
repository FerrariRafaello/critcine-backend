# _ IMPORTS
from app.core.database_users import UserDB
from app.core.exceptions import DuplicateEntryError
from app.users.schemas import UserCreate, UserUpdate, UserPatch, UserOut, UserPublicOut
from app.auth.security import hash_password


# _ Service Class
class UserService:
    def __init__(self, db:UserDB)->None:
        self.db=db

    def create_user(self, payload:UserCreate)->UserOut:
        try:
            row = self.db.create_user(
                name=payload.name,
                age=payload.age,
                email=payload.email,
                cpf=payload.cpf,
                hashed_password=hash_password(payload.password)
            )
            return UserOut(**row, followers_count=0, following_count=0, is_following=False)
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

    def list_users(self, limit: int, offset: int) -> tuple[list[UserPublicOut], int]:
        rows = self.db.list_users(limit=limit, offset=offset)
        total = rows[0]["total_count"] if rows else 0
        items = [
            UserPublicOut(
                id=row["id"],
                name=row["name"],
                bio=row["bio"],
                pronouns=row["pronouns"],
                favorite_genres=row["favorite_genres"],
                avatar_id=row["avatar_id"],
                cover_id=row["cover_id"],
            ) for row in rows
        ]
        return items, total
    

    def get_user(self, user_id: int, follow_stats: dict | None = None) -> UserOut:
        row = self.db.get_user_by_id(user_id)
        if row is None:
            raise LookupError("User not found")

        # follow_stats is fetched by the router and passed in to keep this layer decoupled from follow logic
        stats = follow_stats or {}
        return UserOut(
            id=row["id"],
            name=row["name"],
            age=row["age"],
            email=row["email"],
            cpf=row["cpf"],
            bio=row["bio"],
            pronouns=row["pronouns"],
            favorite_genres=row["favorite_genres"],
            avatar_id=row["avatar_id"],
            cover_id=row["cover_id"],
            followers_count=stats.get("followers_count", 0),
            following_count=stats.get("following_count", 0),
            is_following=stats.get("is_following", False),
        )

    def update_user(
            self,
            user_id:int,
            payload:UserUpdate
    )->None:
        current=self.db.get_user_by_id(user_id)
        if current is None:
            raise LookupError("User not found")

        # CPF is treated as an immutable identifier once set
        if payload.cpf is not None and payload.cpf != current["cpf"]:
            raise ValueError("CPF cannot be changed")

        try:
            updated=self.db.update_user(
                user_id=user_id,
                name=payload.name,
                age=payload.age,
                email=payload.email,
                cpf=payload.cpf,
                bio=payload.bio,
                pronouns=payload.pronouns,
                favorite_genres=payload.favorite_genres,
                avatar_id=payload.avatar_id,
                cover_id=payload.cover_id
            )
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

        if not updated:
            raise LookupError("User not found")

    def patch_user(
            self,
            user_id:int,
            payload:UserPatch
    )-> None:
        current=self.db.get_user_by_id(user_id)
        if current is None:
            raise LookupError("User not found")

        if payload.cpf is not None and payload.cpf != current["cpf"]:
            raise ValueError("CPF cannot be changed")

        try:
            updated=self.db.patch_user(
                user_id=user_id,
                name=payload.name if payload.name is not None else current["name"],
                age=payload.age if payload.age is not None else current["age"],
                email=payload.email if payload.email is not None else current["email"],
                cpf=payload.cpf if payload.cpf is not None else current["cpf"],
                bio=payload.bio if payload.bio is not None else current["bio"],
                pronouns=payload.pronouns if payload.pronouns is not None else current["pronouns"],
                favorite_genres=payload.favorite_genres if payload.favorite_genres is not None else current["favorite_genres"],
                avatar_id=payload.avatar_id if payload.avatar_id is not None else current["avatar_id"],
                cover_id=payload.cover_id if payload.cover_id is not None else current["cover_id"],
            )
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

        if not updated:
            raise LookupError("User not found")

    def delete_user(self, user_id:int)->None:
        deleted = self.db.delete_user(user_id)
        if not deleted:
            raise LookupError("User not found")