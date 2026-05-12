# _ IMPORTS
from fastapi import APIRouter, Query, Depends, Request, status

from app.users.schemas import UserCreate, UserUpdate, UserPatch, UserOut
from app.users.service import UserService
from app.auth.security import get_current_user_id


# _ API Router
router = APIRouter(prefix="/v1/users", tags=["Users"])


# _ Dependency
def get_user_service(request: Request)-> UserService:
    db = request.app.state.db_users
    return UserService(db)


# _ POST
@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user:UserCreate,
    service:UserService=Depends(get_user_service)
)->UserOut:
    return service.create_user(user)


# _ GET ME
@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def get_me(
    service:UserService=Depends(get_user_service),
    current_user_id:int=Depends(get_current_user_id)
)->UserOut:
    return service.get_user(current_user_id)


# _ LIST
@router.get(
    "",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK
)
def list_users(
    limit:int=Query(20, ge=1),
    offset:int=Query(0, ge=0),
    service:UserService=Depends(get_user_service),
    _: int = Depends(get_current_user_id)
)->list[UserOut]:
    return service.list_users(limit=limit, offset=offset)


# _ GET
@router.get(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id:int,
    service:UserService=Depends(get_user_service),
    _: int = Depends(get_current_user_id)
)-> UserOut:
    return service.get_user(user_id)


# _ UPDATE
@router.put(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def update_user(
    user_id:int,
    payload: UserUpdate,
    service:UserService=Depends(get_user_service),
    _: int = Depends(get_current_user_id)
)->UserOut:
    return service.update_user(user_id, payload)


# _ PATCH
@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK
)
def patch_user(
    user_id:int,
    payload:UserPatch,
    service:UserService=Depends(get_user_service),
    _: int = Depends(get_current_user_id)
)->UserOut:
    return service.patch_user(user_id, payload)


# _ DELETE
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id:int,
    service:UserService=Depends(get_user_service),
    _: int = Depends(get_current_user_id)
)->None:
    return service.delete_user(user_id)
