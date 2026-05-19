# _ IMPORTS
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import settings


class FollowDB:
    def __init__(self, db_url: str | None = None, pool: ConnectionPool | None = None):
        if pool is not None:
            self.pool = pool
        else:
            self.db_url = db_url or settings.DATABASE_URL
            if not self.db_url:
                raise RuntimeError("DATABASE_URL is not configured")
            self.pool = ConnectionPool(
                self.db_url,
                min_size=2,
                max_size=10,
                open=True,
                timeout=10,
                kwargs={"row_factory": dict_row}
            )

    def follow(self, follower_id: int, followed_id: int) -> bool:
        """Segue um usuário. Retorna True se o follow foi criado, False se já existia."""
        with self.pool.connection() as conn:
            row = conn.execute(
                """
                INSERT INTO follows (follower_id, followed_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING follower_id
                """,
                (follower_id, followed_id),
            ).fetchone()
            return row is not None

    def unfollow(self, follower_id: int, followed_id: int) -> bool:
        """Deixa de seguir. Retorna True se existia e foi removido."""
        with self.pool.connection() as conn:
            result = conn.execute(
                "DELETE FROM follows WHERE follower_id = %s AND followed_id = %s",
                (follower_id, followed_id),
            )
            return result.rowcount > 0

    def is_following(self, follower_id: int, followed_id: int) -> bool:
        with self.pool.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = %s",
                (follower_id, followed_id),
            ).fetchone()
            return row is not None

    def get_followers(self, user_id: int) -> list[Any]:
        """Retorna lista de usuários que seguem user_id."""
        with self.pool.connection() as conn:
            rows = conn.execute(
                """
                SELECT u.id, u.name, u.avatar_id
                FROM follows f
                JOIN users u ON u.id = f.follower_id
                WHERE f.followed_id = %s
                ORDER BY f.created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def get_following(self, user_id: int) -> list[Any]:
        """Retorna lista de usuários que user_id segue."""
        with self.pool.connection() as conn:
            rows = conn.execute(
                """
                SELECT u.id, u.name, u.avatar_id
                FROM follows f
                JOIN users u ON u.id = f.followed_id
                WHERE f.follower_id = %s
                ORDER BY f.created_at DESC
                """,
                (user_id,),
            ).fetchall()
            return list(rows)

    def get_stats(self, user_id: int, viewer_id: int | None = None) -> dict[str, Any]:
        """Retorna contagens e se viewer segue user_id."""
        with self.pool.connection() as conn:
            row = conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM follows WHERE followed_id = %s) AS followers_count,
                    (SELECT COUNT(*) FROM follows WHERE follower_id = %s) AS following_count,
                    CASE WHEN %s IS NOT NULL THEN
                        EXISTS (SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = %s)
                    ELSE FALSE END AS is_following
                """,
                (user_id, user_id, viewer_id, viewer_id, user_id),
            ).fetchone()
            return dict(row) if row else {"followers_count": 0, "following_count": 0, "is_following": False}

    def close_db_follows(self) -> None:
        self.pool.close()
