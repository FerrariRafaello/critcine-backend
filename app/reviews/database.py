# _ IMPORTS
from typing import Any, Optional, cast

import psycopg
from psycopg import sql
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
        self._ensure_like_support()

    def _ensure_like_support(self)->None:
        with self.pool.connection() as conn:
            conn.execute(
                """
                ALTER TABLE reviews
                ADD COLUMN IF NOT EXISTS likes INTEGER NOT NULL DEFAULT 0
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_likes (
                    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (review_id, user_id)
                )
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

    def get_reviews_by_movie(self, tmdb_movie_id:int, current_user_id:Optional[int]=None)->list[Any]:
        with self.pool.connection() as conn:
            if current_user_id is None:
                rows=conn.execute(
                    """
                    SELECT id, user_id, tmdb_movie_id, rating, comment, likes, FALSE AS liked_by_me, created_at
                    FROM reviews
                    WHERE tmdb_movie_id = %s
                    ORDER BY created_at DESC
                    """,
                    (tmdb_movie_id,),
                ).fetchall()
            else:
                rows=conn.execute(
                    """
                    SELECT r.id, r.user_id, r.tmdb_movie_id, r.rating, r.comment, r.likes,
                           EXISTS (
                               SELECT 1
                               FROM review_likes rl
                               WHERE rl.review_id = r.id AND rl.user_id = %s
                           ) AS liked_by_me,
                           r.created_at
                    FROM reviews r
                    WHERE r.tmdb_movie_id = %s
                    ORDER BY r.created_at DESC
                    """,
                    (current_user_id, tmdb_movie_id),
                ).fetchall()
            return list(rows)

    def get_reviews_by_user(self, user_id:int)->list[Any]:
        with self.pool.connection() as conn:
            rows=conn.execute(
                """
                SELECT id, user_id, tmdb_movie_id, rating, comment, likes, FALSE AS liked_by_me, created_at
                FROM reviews
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def get_review_by_id(self, review_id:int, current_user_id:Optional[int]=None)->dict[str,Any] | None:
        with self.pool.connection() as conn:
            if current_user_id is None:
                row=conn.execute(
                    """
                    SELECT id, user_id, tmdb_movie_id, rating, comment, likes, FALSE AS liked_by_me, created_at
                    FROM reviews
                    WHERE id = %s
                    """,
                    (review_id,),
                ).fetchone()
            else:
                row=conn.execute(
                    """
                    SELECT r.id, r.user_id, r.tmdb_movie_id, r.rating, r.comment, r.likes,
                           EXISTS (
                               SELECT 1
                               FROM review_likes rl
                               WHERE rl.review_id = r.id AND rl.user_id = %s
                           ) AS liked_by_me,
                           r.created_at
                    FROM reviews r
                    WHERE r.id = %s
                    """,
                    (current_user_id, review_id),
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

    def like_review(self, review_id:int, user_id:int)->str:
        with self.pool.connection() as conn:
            exists=conn.execute(
                "SELECT 1 FROM reviews WHERE id = %s",
                (review_id,),
            ).fetchone()
            if exists is None:
                return "not_found"

            inserted=conn.execute(
                """
                INSERT INTO review_likes (review_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (review_id, user_id) DO NOTHING
                RETURNING review_id
                """,
                (review_id, user_id),
            ).fetchone()

            if inserted is None:
                return "already_liked"

            conn.execute(
                """
                UPDATE reviews
                SET likes = likes + 1
                WHERE id = %s
                """,
                (review_id,),
            )
            return "liked"

    def get_all_reviews(
        self,
        current_user_id: int,
        sort: str = "newest",
        search_user: Optional[str] = None,
        search_movie: Optional[int] = None,
        following_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> list[Any]:

        order_col = {
            "newest": sql.SQL("r.created_at DESC"),
            "oldest": sql.SQL("r.created_at ASC"),
            "popular": sql.SQL("r.likes DESC, r.created_at DESC"),
        }.get(sort, sql.SQL("r.created_at DESC"))

        filters = [sql.SQL("1=1")]
        params: list[Any] = [current_user_id]

        if following_only:
            filters.append(sql.SQL(
                "r.user_id IN (SELECT followed_id FROM follows WHERE follower_id = %s)"
            ))
            params.append(current_user_id)

        if search_movie is not None:
            filters.append(sql.SQL("r.tmdb_movie_id = %s"))
            params.append(search_movie)

        if search_user:
            if search_user.isdigit():
                filters.append(sql.SQL("r.user_id = %s"))
                params.append(int(search_user))
            else:
                filters.append(sql.SQL("u.name ILIKE %s"))
                params.append(f"%{search_user}%")

        params += [limit, offset]

        query = sql.SQL("""
            SELECT r.id, r.user_id, r.tmdb_movie_id, r.rating, r.comment, r.likes,
                EXISTS (
                    SELECT 1 FROM review_likes rl
                    WHERE rl.review_id = r.id AND rl.user_id = %s
                ) AS liked_by_me,
                r.created_at,
                u.name AS user_name
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            WHERE {where}
            ORDER BY {order}
            LIMIT %s OFFSET %s
        """).format(
            where=sql.SQL(" AND ").join(filters),
            order=order_col
        )

        with self.pool.connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return list(rows)

    def close_db_reviews(self)->None:
        self.pool.close()
