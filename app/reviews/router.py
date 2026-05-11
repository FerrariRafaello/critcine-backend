# _ IMPORTS
from fastapi import APIRouter, Depends, Request, status

from app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewOut
from app.reviews.service import ReviewService
from app.auth.security import get_current_user_id


# _ Router
router=APIRouter(prefix="/v1/reviews", tags=["Reviews"])


# _ Dependency
def get_review_service(request:Request)->ReviewService:
    db=request.app.state.db_reviews
    return ReviewService(db)


# _ POST
@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    service: ReviewService = Depends(get_review_service),
    current_user_id: int = Depends(get_current_user_id)
) -> ReviewOut:
    return service.create_review(user_id=current_user_id, payload=payload)


# _ GET by movie
@router.get("/movie/{tmdb_movie_id}", response_model=list[ReviewOut])
def get_reviews(
    tmdb_movie_id:int,
    service:ReviewService=Depends(get_review_service),
    current_user_id:int=Depends(get_current_user_id)
)->list[ReviewOut]:
    return service.get_reviews_by_movie(tmdb_movie_id, current_user_id)


# _ Get by user
@router.get("/user/{user_id}", response_model=list[ReviewOut])
def get_reviews_by_user(
    user_id:int,
    service:ReviewService=Depends(get_review_service),
    _:int=Depends(get_current_user_id)
)->list[ReviewOut]:
    return service.get_reviews_by_user(user_id)


# _ PATCH
@router.patch("/{review_id}", response_model=ReviewOut)
def update_review(
    review_id:int,
    payload:ReviewUpdate,
    service:ReviewService=Depends(get_review_service),
    current_user_id:int=Depends(get_current_user_id)
)->ReviewOut:
    return service.update_review(
        review_id=review_id,
        user_id=current_user_id,
        payload=payload
    )


# _ DELETE
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id:int,
    service:ReviewService=Depends(get_review_service),
    current_user_id:int=Depends(get_current_user_id)
)->None:
    service.delete_review(review_id=review_id, user_id=current_user_id)


@router.post("/{review_id}/like", response_model=ReviewOut)
def like_review(
    review_id:int,
    service:ReviewService=Depends(get_review_service),
    current_user_id:int=Depends(get_current_user_id)
)->ReviewOut:
    return service.like_review(review_id, current_user_id)