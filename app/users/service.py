# _ IMPORTS
from app.core.database_users import UserDB
from app.core.exceptions import DuplicateEntryError
from app.users.schemas import UserCreate, UserUpdate, UserPatch, UserOut
from app.auth.security import hash_password


# _ Service Class
class UserService:
    def __init__(self, db:UserDB)->None:
        self.db=db

    def create_user(self, payload:UserCreate)->UserOut:
        try:
            user_id = self.db.create_user(
                name=payload.name,
                age=payload.age,
                email=payload.email,
                cpf=payload.cpf,
                hashed_password=hash_password(payload.password)
            )
            return self.get_user(user_id)
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

    def list_users(self, limit:int, offset:int) -> list[UserOut]:
        rows = self.db.list_users(limit=limit, offset=offset)

        return[
            UserOut(
                id=row["id"],
                name=row["name"],
                age=row["age"],
                email=row["email"],
                cpf=row["cpf"],
                bio=row["bio"],
                pronouns=row["pronouns"],
                favorite_genres=row["favorite_genres"],
                avatar_id=row["avatar_id"],
                cover_id=row["cover_id"]
            ) for row in rows
        ]

    def get_user(self, user_id:int) -> UserOut:
        row = self.db.get_user_by_id(user_id)
        if row is None:
            raise LookupError("User not found")

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
            cover_id=row["cover_id"]
        )

    def update_user(
            self,
            user_id:int,
            payload:UserUpdate
    )->UserOut:
        current=self.db.get_user_by_id(user_id)
        if current is None:
            raise LookupError("User not found")

        if payload.cpf is not None and payload.cpf != current["cpf"]:
            raise ValueError("CPF cannot be changed")

        try:
            updated=self.db.update_user(
                user_id=user_id,
                name=payload.name,
                age=payload.age,
                email=payload.email,
                cpf=payload.cpf
            )
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

        if not updated:
            raise LookupError("User not found")

        return self.get_user(user_id)

    def patch_user(
            self,
            user_id:int,
            payload:UserPatch
    )-> UserOut:
        current=self.db.get_user_by_id(user_id)
        if current is None:
            raise LookupError("User not found")

        try:
            updated=self.db.patch_user(
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

        return self.get_user(user_id)

    def delete_user(self, user_id:int)->None:
        deleted = self.db.delete_user(user_id)
        if not deleted:
            raise LookupError("User not found")