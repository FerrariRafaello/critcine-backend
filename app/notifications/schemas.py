# _ IMPORTS
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    from_user_id: int
    from_user_name: str
    from_user_avatar: Optional[str] = None
    type: str
    entity_id: Optional[int] = None
    read: bool
    created_at: datetime
