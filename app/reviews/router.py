import os
from typing import Optional
from fastapi import APIRouter, Depends, Request, status, Query

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewOut, ReviewOutFull
from app.reviews.service import ReviewService
from app.auth.security import get_current_user_id
from app.core.schemas import PageOut


router = APIRouter(prefix="/v1/reviews", tags=["Reviews"])
limiter = Limiter(key_func=get_remote_address)


def get_write_limit() -> str:
    return "1000/minute" if os.getenv("TESTING") else "20/minute"


def get_review_service(request: Request) -> ReviewService:
    db = request.app.state.db_reviews
    return ReviewService(db)


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_write_limit)
def create_review(
    request: Request,
    payload: ReviewCreate,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> ReviewOut:
    return service.create_review(user_id=current_user_id, payload=payload)


@router.get("/movie/{tmdb_movie_id}", response_model=list[ReviewOut])
def get_reviews(
    tmdb_movie_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> list[ReviewOut]:
    return service.get_reviews_by_movie(tmdb_movie_id, current_user_id)


@router.get("/user/{user_id}", response_model=list[ReviewOut])
def get_reviews_by_user(
    user_id: int,
    service: ReviewService = Depends(get_review_service),
    _: int = Depends(get_current_user_id)
) -> list[ReviewOut]:
    return service.get_reviews_by_user(user_id)


@router.get("/feed", response_model=PageOut[ReviewOutFull])
def get_all_reviews(
    sort: str = Query("newest", pattern="^(newest|oldest|popular)$"),
    search_user: Optional[str] = Query(None, max_length=100),
    search_movie: Optional[int] = Query(None),
    # when true, only shows reviews from users the current user follows
    following_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=50),
    offset: int = Query(0, ge=0),
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> PageOut[ReviewOutFull]:
    items, total = service.get_all_reviews(
        current_user_id=current_user_id,
        sort=sort,
        search_user=search_user,
        search_movie=search_movie,
        following_only=following_only,
        limit=limit,
        offset=offset
    )
    return  PageOut(data=items, total=total, limit=limit, offset=offset)



@router.patch("/{review_id}", response_model=ReviewOut)
@limiter.limit(get_write_limit)
def update_review(
    request: Request,
    review_id: int,
    payload: ReviewUpdate,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> ReviewOut:
    return service.update_review(
        review_id=review_id,
        user_id=current_user_id,
        payload=payload
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> None:
    service.delete_review(review_id=review_id, user_id=current_user_id)


@router.post("/{review_id}/like", response_model=ReviewOut)
@limiter.limit(get_write_limit)
def like_review(
    request: Request,
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> ReviewOut:
    return service.like_review(review_id, current_user_id)


@router.delete("/{review_id}/like", response_model=ReviewOut)
@limiter.limit(get_write_limit)
def unlike_review(
    request: Request,
    review_id: int,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> ReviewOut:
    return service.unlike_review(review_id, current_user_id)
