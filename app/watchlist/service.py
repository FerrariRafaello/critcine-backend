# _ IMPORTS
from app.watchlist.database import WatchlistDB
from app.watchlist.schemas import WatchlistCreate, WatchlistUpdate, WatchlistOut
from app.core.exceptions import DuplicateEntryError


# _ Service CLass
class WatchlistService:
    def __init__(self, db:WatchlistDB)->None:
        self.db=db

    def add_to_watchlist(
            self,
            user_id:int,
            payload:WatchlistCreate
    )->WatchlistOut:
        try:
            item_id=self.db.add_to_watchlist(
                user_id=user_id,
                tmdb_movie_id=payload.tmdb_movie_id,
                status=payload.status
            )
            return self.get_item(item_id)
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

    def get_watchlist(self, user_id:int)-> list[WatchlistOut]:
        rows=self.db.get_watchlist_by_user(user_id)
        return [WatchlistOut(**row) for row in rows]

    def get_item(self, item_id:int)->WatchlistOut:
        row=self.db.get_watchlist_item(item_id)
        if row is None:
            raise LookupError("Watchlist item not found")
        return WatchlistOut(**row)

    def update_item(
            self,
            item_id:int,
            user_id:int,
            payload:WatchlistUpdate
    )->WatchlistOut:
        item=self.db.get_watchlist_item(item_id)
        if item is None:
            raise LookupError("Watchlist item not found")
        if item["user_id"] != user_id:
            raise PermissionError("Not allowed to edit this item")

        updated=self.db.update_watchlist_item(
            item_id=item_id,
            status=payload.status
        )
        if not updated:
            raise LookupError("Watchlist item not found")
        return self.get_item(item_id)

    def delete_item(self, item_id:int, user_id:int)->None:
        item=self.db.get_watchlist_item(item_id)
        if item is None:
            raise LookupError("Watchlist item not found")
        if item["user_id"] != user_id:
            raise PermissionError("Not allowed to delete this item")
        self.db.delete_watchlist_item(item_id)
