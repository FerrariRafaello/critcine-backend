# _ IMPORTS
from typing import Any, Optional, cast


import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


from app.core.config import settings
from app.core.exceptions import DuplicateEntryError


# _ DB Class
class WatchlistDB:
    def __init__(
            self,
            db_url:str | None=None,
            pool:ConnectionPool | None=None
    ):
        if pool is not None:
            self.pool=pool
        else:
            self.db_url=db_url or settings.DATABASE_URL
            if not self.db_url:
                raise RuntimeError("DATABASE_URL it not configured")
            self.pool=ConnectionPool(
                self.db_url,
                min_size=2,
                max_size=10,
                open=True,
                kwargs={"row_factory":dict_row}
            )

    def add_to_watchlist(
            self,
            user_id:int,
            tmdb_movie_id:int,
            status:str="want_to_watch"
    )->int:
        try:
            with self.pool.connection() as conn:
                row=conn.execute(
                     """
                    INSERT INTO watchlist(user_id, tmdb_movie_id, status)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, tmdb_movie_id, status,),
                ).fetchone()
                return cast(dict[str, Any], row)["id"]
        except psycopg.IntegrityError:
            raise DuplicateEntryError("Movie already in watchlist")

    def get_watchlist_by_user(self, user_id:int)->list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, status, created_at
                FROM watchlist
                WHERE user_id=%s
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def get_watchlist_item(self, item_id:int)->dict[str,Any] | None:
        with self.pool.connection() as conn:
            row=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, status, created_at
                FROM watchlist
                WHERE id=%s
                """,
                (item_id,),
            ).fetchone()
            return cast(dict[str, Any] | None, row)

    def update_watchlist_item(
            self,
            item_id:int,
            status:str
    )->bool:
        with self.pool.connection() as conn:
            result=conn.execute(
                """
                UPDATE watchlist
                SET status=%s
                WHERE id=%s
                """,
                (status, item_id,),
            )
            return result.rowcount > 0

    def delete_watchlist_item(self, item_id:int)->bool:
        with self.pool.connection() as conn:
            result=conn.execute(
                "DELETE FROM watchlist WHERE id=%s",
                (item_id,),
            )
            return result.rowcount > 0

    def close_db_watchlist(self)->None:
        self.pool.close()
