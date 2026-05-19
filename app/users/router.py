# _ IMPORTS
import os
from fastapi import APIRouter, Query, Depends, Request, status, HTTPException

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.users.schemas import UserCreate, UserUpdate, UserPatch, UserOut
from app.users.service import UserService
from app.follows.database import FollowDB
from app.auth.security import get_current_user_id
from app.core.ip_limits import check_registration_limit, record_registration


# _ API Router
router = APIRouter(prefix="/v1/users", tags=["Users"])
limiter = Limiter(key_func=get_remote_address)


def get_register_limit() -> str:
    return "1000/minute" if os.getenv("TESTING") else "3/minute"


# _ Dependencies
def get_user_service(request: Request) -> UserService:
    return UserService(request.app.state.db_users)

def get_follow_db(request: Request) -> FollowDB:
    return request.app.state.db_follows

def _require_owner(current_user_id: int, user_id: int) -> None:
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify another user's profile"
        )


# _ POST
@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit(get_register_limit)
def create_user(
    request: Request,
    user: UserCreate,
    service: UserService = Depends(get_user_service)
) -> UserOut:
    if not os.getenv("TESTING"):
        ip = get_remote_address(request)
        blocked, hours_remaining = check_registration_limit(ip)
        if blocked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account creation limit reached for this IP. Try again in {hours_remaining}h."
            )
        result = service.create_user(user)
        record_registration(ip)
        return result
    return service.create_user(user)


# _ GET ME
@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def get_me(
    service: UserService = Depends(get_user_service),
    follow_db: FollowDB = Depends(get_follow_db),
    current_user_id: int = Depends(get_current_user_id)
) -> UserOut:
    stats = follow_db.get_stats(current_user_id, viewer_id=current_user_id)
    return service.get_user(current_user_id, follow_stats=stats)


# _ LIST
@router.get(
    "",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK
)
def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: UserService = Depends(get_user_service),
    _: int = Depends(get_current_user_id)
) -> list[UserOut]:
    return service.list_users(limit=limit, offset=offset)


# _ GET
@router.get(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    follow_db: FollowDB = Depends(get_follow_db),
    current_user_id: int = Depends(get_current_user_id)
) -> UserOut:
    stats = follow_db.get_stats(user_id, viewer_id=current_user_id)
    return service.get_user(user_id, follow_stats=stats)


# _ UPDATE
@router.put(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
    follow_db: FollowDB = Depends(get_follow_db),
    current_user_id: int = Depends(get_current_user_id)
) -> UserOut:
    _require_owner(current_user_id, user_id)
    service.update_user(user_id, payload)
    stats = follow_db.get_stats(user_id, viewer_id=current_user_id)
    return service.get_user(user_id, follow_stats=stats)


# _ PATCH
@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def patch_user(
    user_id: int,
    payload: UserPatch,
    service: UserService = Depends(get_user_service),
    follow_db: FollowDB = Depends(get_follow_db),
    current_user_id: int = Depends(get_current_user_id)
) -> UserOut:
    _require_owner(current_user_id, user_id)
    service.patch_user(user_id, payload)
    stats = follow_db.get_stats(user_id, viewer_id=current_user_id)
    return service.get_user(user_id, follow_stats=stats)


# _ DELETE
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user_id: int = Depends(get_current_user_id)
) -> None:
    _require_owner(current_user_id, user_id)
    return service.delete_user(user_id)
