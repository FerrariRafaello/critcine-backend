# _ IMPORTS
from typing import Any, Optional, cast

from app.reviews.database import ReviewDB
from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewOut, ReviewOutFull
from app.core.exceptions import DuplicateEntryError


# _ Service Class
class ReviewService:
    def __init__(self, db:ReviewDB)->None:
        self.db=db

    def create_review(self, user_id:int, payload:ReviewCreate)->ReviewOut:
        try:
            row=self.db.create_review(
                user_id=user_id,
                tmdb_movie_id=payload.tmdb_movie_id,
                rating=payload.rating,
                comment=payload.comment
            )
            return ReviewOut(**row)
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

    def get_reviews_by_movie(self, tmdb_movie_id:int, current_user_id:int)->list[ReviewOut]:
        rows=self.db.get_reviews_by_movie(tmdb_movie_id, current_user_id)
        return [ReviewOut(**row) for row in rows]

    def get_reviews_by_user(self, user_id:int)->list[ReviewOut]:
        rows=self.db.get_reviews_by_user(user_id)
        return [ReviewOut(**row) for row in rows]

    def get_review(self, review_id: int, current_user_id:int | None=None) -> ReviewOut:
        row = self.db.get_review_by_id(review_id, current_user_id)
        if row is None:
            raise LookupError("Review not found")
        return ReviewOut(**row)

    def update_review(
            self,
            review_id:int,
            user_id:int,
            payload:ReviewUpdate
    )-> ReviewOut:
        review=self.db.get_review_by_id(review_id)
        if review is None:
            raise LookupError("Review not found")
        # only the review author can edit it
        if review["user_id"] != user_id:
            raise PermissionError("Not allowed to edit this review")

        updated=self.db.update_review(
            review_id=review_id,
            rating=payload.rating if payload.rating is not None else review["rating"],
            comment=payload.comment if payload.comment is not None else review["comment"],
        )
        if updated is None:
            raise LookupError("Review not found")
        return ReviewOut(**updated)

    def delete_review(
            self,
            review_id:int,
            user_id:int
    )->None:
        review=self.db.get_review_by_id(review_id)
        if review is None:
            raise LookupError("Review not found")
        # only the review author can delete it
        if review["user_id"] != user_id:
            raise PermissionError("Not allowed to delete this review")
        self.db.delete_review(review_id)

    def like_review(self, review_id:int, user_id:int)->ReviewOut:
        result=self.db.like_review(review_id, user_id)
        if result == "not_found":
            raise LookupError("Review not found")
        if result == "already_liked":
            raise ValueError("You already liked this review")
        return ReviewOut(**cast(dict[str, Any], result))

    def unlike_review(self, review_id: int, user_id: int) -> ReviewOut:
        result = self.db.unlike_review(review_id, user_id)
        if result == "not_found":
            raise LookupError("Review not found")
        if result == "not_liked":
            raise ValueError("You have not liked this review")
        return ReviewOut(**cast(dict[str, Any], result))

    def get_all_reviews(
        self,
        current_user_id: int,
        sort: str = "newest",
        search_user: Optional[str] = None,
        search_movie: Optional[int] = None,
        following_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[ReviewOutFull], int]:
        rows, total = self.db.get_all_reviews(
            current_user_id=current_user_id,
            sort=sort,
            search_user=search_user,
            search_movie=search_movie,
            following_only=following_only,
            limit=limit,
            offset=offset
        )
        return [ReviewOutFull(**row) for row in rows], total