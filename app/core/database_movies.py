# _ IMPORTS
from typing import Any, Optional, cast

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg import Connection

from app.core.exceptions import DuplicateEntryError
from app.core.config import settings


# _ DB Class
class MovieDB:
    def __init__(self,
                 db_url: str | None = None,
                 pool: ConnectionPool[Connection] | None=None
                 ):
        # accept an external pool so tests can inject a shared test connection
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
                kwargs={"row_factory": dict_row}
            )


    def create_movie(
            self,
            name:str,
            year:int,
            rating:Optional[float]=None
    ) -> int:
        try:
            with self.pool.connection() as conn:
                row=conn.execute(
                    """
                    INSERT INTO movies(
                        name, year, rating
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (name, year, rating),
                ).fetchone()
                return cast(dict[str, Any],row)["id"]
        except psycopg.IntegrityError:
            raise DuplicateEntryError("Movie already exists")

    def get_movies(self, limit:int, offset:int) -> list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, name, year, rating
                FROM movies
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (limit, offset,),
            ).fetchall()
            return list(rows)

    def get_movie_by_id(self, movie_id: int) -> dict[str, Any] | None:
        with self.pool.connection() as conn:
            row= conn.execute(
                """
                SELECT id, name, year, rating
                FROM movies
                WHERE id=%s
                """,
                (movie_id,),
            ).fetchone()
            return cast(dict[str,Any] | None, row)

    def update_movie(
            self,
            movie_id:int,
            name:str,
            year:int,
            rating:Optional[float]=None
    ) -> bool:
        try:
            with self.pool.connection() as conn:
                result=conn.execute(
                    """
                    UPDATE movies
                    SET name=%s, year=%s, rating=%s
                    WHERE id=%s
                    """,
                    (name,year, rating, movie_id,),
                )
                return result.rowcount > 0
        except psycopg.IntegrityError:
            raise DuplicateEntryError("Movie already exists")

    def patch_movie(
            self,
            movie_id:int,
            name:Optional[str]=None,
            year:Optional[int]=None,
            rating:Optional[float]=None,
    ) -> bool:
        # fetch current values so None fields fall back to what's already stored
        current = self.get_movie_by_id(movie_id)
        if current is None:
            return False

        try:
            with self.pool.connection() as conn:
                result=conn.execute(
                    """
                    UPDATE movies
                    SET name=%s,
                        year=%s,
                        rating=%s
                    WHERE id=%s
                    """,
                    (
                        name if name is not None else current["name"],
                        year if year is not None else current["year"],
                        rating if rating is not None else current["rating"],
                        movie_id,
                    ),
                )
                return result.rowcount > 0
        except psycopg.IntegrityError:
            raise DuplicateEntryError("Movie already exists")

    def delete_movie(self, movie_id:int) -> bool:
        with self.pool.connection() as conn:
            result=conn.execute(
                """
                DELETE FROM movies
                WHERE id=%s
                """,
                (movie_id,),
            )
            return result.rowcount > 0

    def close_db_movies(self) -> None:
        self.pool.close()
