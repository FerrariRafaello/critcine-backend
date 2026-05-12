# _ IMPORTS
from typing import Any, Optional, cast

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg import Connection

from app.core.exceptions import DuplicateEntryError
from app.core.config import settings


# _ DB Class
class UserDB:
    def __init__(self,
                 db_url:str | None=None,
                 pool:ConnectionPool[Connection] | None=None):
        if pool is not None:
            self.pool=pool
        else:
            self.db_url=db_url or settings.DATABASE_URL
            if not self.db_url:
                raise RuntimeError("DATABASE_URL is not configured")

            self.pool=ConnectionPool(
                self.db_url,
                min_size=2,
                max_size=10,
                open=True,
                timeout=10,
                kwargs={"row_factory": dict_row})

    def create_user(
            self,
            name:str,
            email:str,
            age:Optional[int]=None,
            cpf:Optional[str]=None,
            hashed_password:str=''
    ) -> int:
        try:
            with self.pool.connection() as conn:
                row = conn.execute(
                    """
                    INSERT INTO users(
                        name, age, email, cpf, hashed_password
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    RETURNING id
                    """,
                    (name, age, email, cpf, hashed_password,),
                ).fetchone()
                return cast(dict[str, Any], row)["id"]
        except psycopg.IntegrityError:
            raise DuplicateEntryError("CPF or email already exists")

    def list_users(self, limit:int, offset:int) -> list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, name, age, email, cpf, bio, pronouns, favorite_genres, avatar_id, cover_id 
                FROM users
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (limit, offset,),
            ).fetchall()
            return list(rows)

    def get_user_by_id(self, user_id:int) -> dict[str, Any] | None:
        with self.pool.connection() as conn:
            row=conn.execute(
                """
                SELECT id, name, age, email, cpf, bio, pronouns, favorite_genres, avatar_id, cover_id
                FROM users
                WHERE id=%s
                """,
                (user_id,),
            ).fetchone()
            return cast(dict[str, Any] | None, row)

    def get_user_by_email(self, email:str)-> dict[str, Any] | None:
        with self.pool.connection() as conn:
            row=conn.execute(
                """
                SELECT id, name, age, email, cpf, hashed_password, bio, pronouns, favorite_genres, avatar_id, cover_id
                FROM users
                WHERE email=%s
                """,
                (email,),
            ).fetchone()
            return cast(dict[str, Any] | None, row)

    def update_user(
            self,
            user_id:int,
            name:str,
            email:str,
            age:Optional[int]=None,
            cpf:Optional[str]=None
    ) -> bool:
        try:
            with self.pool.connection() as conn:
                result=conn.execute(
                    """
                    UPDATE users
                    SET name=%s, age=%s, email=%s, cpf=%s
                    WHERE id=%s
                    """,
                    (name, age, email, cpf, user_id),
                )
                return result.rowcount > 0
        except psycopg.IntegrityError:
            raise DuplicateEntryError("CPF or email already exists")

    def patch_user(
        self,
        user_id:int,
        name:Optional[str]=None,
        age: Optional[int]=None,
        email:Optional[str]=None,
        cpf: Optional[str]=None,
        bio: Optional[str]=None,
        avatar_id: Optional[str]=None,
        cover_id: Optional[str]=None,
        pronouns: Optional[str]=None,
        favorite_genres: Optional[str]=None
) -> bool:
        current = self.get_user_by_id(user_id)
        if current is None:
            return False

        try:
            with self.pool.connection() as conn:
                result=conn.execute(
                    """
                    UPDATE users
                    SET name=%s,
                        age=%s,
                        email=%s,
                        cpf=%s,
                        bio=%s,
                        avatar_id=%s,
                        cover_id=%s,
                        pronouns=%s,
                        favorite_genres=%s
                    WHERE id=%s
                    """,
                    (
                        name if name is not None else current["name"],
                        age if age is not None else current["age"],
                        email if email is not None else current["email"],
                        cpf if cpf is not None else current["cpf"],
                        bio if bio is not None else current["bio"],
                        avatar_id if avatar_id is not None else current["avatar_id"],
                        cover_id if cover_id is not None else current["cover_id"],
                        pronouns if pronouns is not None else current["pronouns"],
                        favorite_genres if favorite_genres is not None else current["favorite_genres"],
                        user_id,
                    ),
                )
                return result.rowcount > 0
        except psycopg.IntegrityError:
            raise DuplicateEntryError("CPF or email already exists")

    def delete_user(self, user_id:int) -> bool:
        with self.pool.connection() as conn:
            result = conn.execute(
                "DELETE FROM users WHERE id=%s",
                (user_id,),
            )
            return result.rowcount > 0

    def close_db_users(self)->None:
        self.pool.close()
