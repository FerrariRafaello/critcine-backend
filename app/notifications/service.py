# _ IMPORTS
from typing import Optional

from app.notifications.database import NotificationDB
from app.notifications.schemas import NotificationOut


# _ Service Class
class NotificationService:
    def __init__(self, db: NotificationDB) -> None:
        self.db = db

    def get_notifications(self, user_id: int, limit: int, offset: int) -> list[NotificationOut]:
        rows = self.db.get_by_user(user_id, limit, offset)
        return [NotificationOut(**row) for row in rows]

    def mark_read(self, notification_id: int, user_id: int) -> None:
        found = self.db.mark_read(notification_id, user_id)
        if not found:
            raise LookupError("Notification not found")
