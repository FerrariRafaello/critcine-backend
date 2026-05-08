# _ IMPORTS
from fastapi import APIRouter, Depends, Request, status


from app.watchlist.schemas import WatchlistCreate, WatchlistUpdate, WatchlistOut
from app.watchlist.service import WatchlistService
from app.auth.security import get_current_user_id


# _ Router
router=APIRouter(prefix="/v1/watchlist", tags=["Watchlist"])


# _ Dependency
def get_watchlist_service(request:Request)->WatchlistService:
    db=request.app.state.db_watchlist
    return WatchlistService(db)


# _ POST
@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    payload:WatchlistCreate,
    service:WatchlistService=Depends(get_watchlist_service),
    current_user_id:int=Depends(get_current_user_id)
)->WatchlistOut:
    return service.add_to_watchlist(user_id=current_user_id, payload=payload)


# _ GET
@router.get("", response_model=list[WatchlistOut])
def get_watchlist(
    service:WatchlistService=Depends(get_watchlist_service),
    current_user_id:int=Depends(get_current_user_id)
)->list[WatchlistOut]:
    return service.get_watchlist(current_user_id)


# _ PATCH
@router.patch("/{item_id}", response_model=WatchlistOut)
def update_item(
    item_id:int,
    payload:WatchlistUpdate,
    service:WatchlistService=Depends(get_watchlist_service),
    current_user_id:int=Depends(get_current_user_id)
)->WatchlistOut:
    return service.update_item(
        item_id=item_id,
        user_id=current_user_id,
        payload=payload
    )


# _ DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id:int,
    service:WatchlistService=Depends(get_watchlist_service),
    current_user_id:int=Depends(get_current_user_id)
)->None:
    service.delete_item(item_id=item_id, user_id=current_user_id)
