# _ IMPORTS
from fastapi import APIRouter, Depends, Query, Request, status

from app.auth.security import get_current_user_id
from app.notifications.database import NotificationDB
from app.notifications.schemas import NotificationOut
from app.notifications.service import NotificationService


router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


def get_notification_service(request: Request) -> NotificationService:
    return NotificationService(request.app.state.db_notifications)


@router.get("", response_model=list[NotificationOut], status_code=status.HTTP_200_OK)
def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: NotificationService = Depends(get_notification_service),
    current_user_id: int = Depends(get_current_user_id),
) -> list[NotificationOut]:
    return service.get_notifications(current_user_id, limit, offset)


@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_read(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    service.mark_read(notification_id, current_user_id)
