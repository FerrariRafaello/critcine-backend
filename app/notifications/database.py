# _ IMPORTS
from typing import Any, Optional, cast

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import settings


# _ DB Class
class NotificationDB:
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
                kwargs={"row_factory": dict_row},
            )
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.pool.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id              SERIAL PRIMARY KEY,
                    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    from_user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    type            VARCHAR(50) NOT NULL,
                    entity_id       INTEGER,
                    read            BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_notifications_user_id
                ON notifications(user_id, created_at DESC)
                """
            )

    def create(
        self,
        user_id: int,
        from_user_id: int,
        type: str,
        entity_id: Optional[int] = None,
    ) -> None:
        with self.pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO notifications (user_id, from_user_id, type, entity_id)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, from_user_id, type, entity_id),
            )

    def get_by_user(self, user_id: int, limit: int, offset: int) -> list[Any]:
        with self.pool.connection() as conn:
            rows = conn.execute(
                """
                SELECT n.id, n.from_user_id, u.name AS from_user_name,
                       u.avatar_id AS from_user_avatar,
                       n.type, n.entity_id, n.read, n.created_at
                FROM notifications n
                JOIN users u ON u.id = n.from_user_id
                WHERE n.user_id = %s
                ORDER BY n.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset),
            ).fetchall()
            return list(rows)

    def mark_read(self, notification_id: int, user_id: int) -> bool:
        with self.pool.connection() as conn:
            result = conn.execute(
                """
                UPDATE notifications
                SET read = TRUE
                WHERE id = %s AND user_id = %s
                """,
                (notification_id, user_id),
            )
            return result.rowcount > 0

    def close_db_notifications(self) -> None:
        self.pool.close()
