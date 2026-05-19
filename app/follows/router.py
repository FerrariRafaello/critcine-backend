# _ IMPORTS
from fastapi import APIRouter, Depends, Request, status

from app.follows.schemas import FollowUserOut, FollowStatsOut
from app.follows.service import FollowService
from app.auth.security import get_current_user_id


router = APIRouter(prefix="/v1/users", tags=["Follows"])


def get_follow_service(request: Request) -> FollowService:
    return FollowService(request.app.state.db_follows)


# _ POST — seguir
@router.post(
    "/{user_id}/follow",
    response_model=FollowStatsOut,
    status_code=status.HTTP_200_OK
)
def follow_user(
    user_id: int,
    service: FollowService = Depends(get_follow_service),
    current_user_id: int = Depends(get_current_user_id)
) -> FollowStatsOut:
    return service.follow(follower_id=current_user_id, followed_id=user_id)


# _ DELETE — deixar de seguir
@router.delete(
    "/{user_id}/follow",
    response_model=FollowStatsOut,
    status_code=status.HTTP_200_OK
)
def unfollow_user(
    user_id: int,
    service: FollowService = Depends(get_follow_service),
    current_user_id: int = Depends(get_current_user_id)
) -> FollowStatsOut:
    return service.unfollow(follower_id=current_user_id, followed_id=user_id)


# _ GET — seguidores de um usuário
@router.get(
    "/{user_id}/followers",
    response_model=list[FollowUserOut]
)
def get_followers(
    user_id: int,
    service: FollowService = Depends(get_follow_service),
    _: int = Depends(get_current_user_id)
) -> list[FollowUserOut]:
    return service.get_followers(user_id)


# _ GET — quem um usuário segue
@router.get(
    "/{user_id}/following",
    response_model=list[FollowUserOut]
)
def get_following(
    user_id: int,
    service: FollowService = Depends(get_follow_service),
    _: int = Depends(get_current_user_id)
) -> list[FollowUserOut]:
    return service.get_following(user_id)
