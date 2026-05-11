# _ IMPORTS
from typing import Any, Optional, cast

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import settings
from app.core.exceptions import DuplicateEntryError


# _ DB Class
class ReviewDB:
    def __init__(
            self,
            db_url:str | None=None,
            pool:ConnectionPool | None=None
    ):
        if pool is not None:
            self.pool = pool
        else:
            self.db_url=db_url or settings.DATABASE_URL
            if not self.db_url:
                raise RuntimeError("DATABASE_URL is no configured")
            self.pool=ConnectionPool(
                self.db_url,
                min_size=2,
                max_size=10,
                open=True,
                timeout=10,
                kwargs={"row_factory": dict_row}
            )
        self._ensure_likes_column()

    def _ensure_likes_column(self)->None:
        with self.pool.connection() as conn:
            conn.execute(
                """
                ALTER TABLE reviews
                ADD COLUMN IF NOT EXISTS likes INTEGER NOT NULL DEFAULT 0
                """
            )

    def create_review(
            self,
            user_id:int,
            tmdb_movie_id:int,
            rating:float,
            comment:Optional[str]=None
    )->int:
        try:
            with self.pool.connection() as conn:
                row=conn.execute(
                    """
                    INSERT INTO reviews(user_id, tmdb_movie_id, rating, comment)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, tmdb_movie_id, rating, comment,),
                ).fetchone()
                return cast(dict[str, Any], row)["id"]
        except psycopg.IntegrityError:
            raise DuplicateEntryError("Review already exists for this movie")

    def get_reviews_by_movie(self, tmdb_movie_id:int)->list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, rating, comment, likes, created_at
                FROM reviews
                WHERE tmdb_movie_id = %s
                ORDER BY created_at DESC
                """,
                (tmdb_movie_id,),
            ).fetchall()
            return list(rows)

    def get_reviews_by_user(self, user_id:int)->list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, rating, comment, likes, created_at
                FROM reviews
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def get_review_by_id(self, review_id:int)->dict[str,Any] | None:
        with self.pool.connection() as conn:
            row=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, rating, comment, likes, created_at
                FROM reviews
                WHERE id = %s
                """,
                (review_id,),
            ).fetchone()
            return cast(dict[str,Any] | None, row)

    def update_review(
            self,
            review_id:int,
            rating:Optional[float]=None,
            comment:Optional[str]=None
    )->bool:
        current=self.get_review_by_id(review_id)
        if current is None:
            return False

        with self.pool.connection() as conn:
            result=conn.execute(
                """
                UPDATE reviews
                SET rating=%s, comment=%s
                WHERE id=%s
                """,
                (
                    rating if rating is not None else current["rating"],
                    comment if comment is not None else current["comment"],
                    review_id,
                ),
            )
        return result.rowcount > 0

    def delete_review(self,review_id:int)->bool:
        with self.pool.connection() as conn:
            result=conn.execute(
                "DELETE FROM reviews WHERE id=%s",
                (review_id,),
            )
            return result.rowcount > 0

    def like_review(self, review_id:int)->bool:
        with self.pool.connection() as conn:
            result=conn.execute(
                """
                UPDATE reviews
                SET likes = likes + 1
                WHERE id = %s
                """,
                (review_id,),
            )
            return result.rowcount > 0

    def close_db_reviews(self)->None:
        self.pool.close()
