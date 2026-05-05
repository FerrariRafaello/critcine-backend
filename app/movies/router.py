# _ IMPORTS
from fastapi import APIRouter, status, Request, Query, Depends

from app.movies.schemas import CreateMovie, MovieUpdate, MoviePatch, MovieOut
from app.movies.service import MovieService
from app.auth.security import get_current_user_id


# _ API Router
router = APIRouter(prefix="/v1/movies", tags=["Movies"])

# _ Dependency
def get_movie_service(request:Request)-> MovieService:
    db = request.app.state.db_movies
    return MovieService(db)


# _ POST
@router.post(
    "",
    response_model=MovieOut,
    status_code=status.HTTP_201_CREATED
)
def create_movie(
    movie: CreateMovie,
    service: MovieService = Depends(get_movie_service),
    _:int=Depends(get_current_user_id)
)-> MovieOut:
    return service.create_movie(movie)


# _ LIST
@router.get(
    "",
    response_model=list[MovieOut],
    status_code=status.HTTP_200_OK
)
def list_movies(
    limit:int=Query(20, ge=1, le=100),
    offset:int=Query(0, ge=0),
    service:MovieService=Depends(get_movie_service),
     _: int = Depends(get_current_user_id)
)-> list[MovieOut]:
    return service.list_movies(limit=limit, offset=offset)


# _ GET
@router.get(
    "/{movie_id}",
    response_model=MovieOut,
    status_code=status.HTTP_200_OK
)
def get_movie(
    movie_id:int,
    service: MovieService = Depends(get_movie_service),
     _: int = Depends(get_current_user_id)
)->MovieOut:
    return service.get_movie(movie_id)


# _ UPDATE
@router.put(
    "/{movie_id}",
    response_model=MovieOut,
    status_code=status.HTTP_200_OK
)
def update_movie(
    movie_id: int,
    payload: MovieUpdate,
    service: MovieService = Depends(get_movie_service),
    _:int=Depends(get_current_user_id)
) -> MovieOut:
    return service.update_movie(movie_id, payload)


# _ PATCH
@router.patch(
    "/{movie_id}",
    response_model=MovieOut,
    status_code=status.HTTP_200_OK
)
def patch_movie(
    movie_id:int,
    payload:MoviePatch,
    service:MovieService=Depends(get_movie_service),
    _:int=Depends(get_current_user_id)
)-> MovieOut:
    return service.patch_movie(movie_id, payload)


# _ DELETE
@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_movie(
    movie_id:int,
    service:MovieService=Depends(get_movie_service),
    _:int=Depends(get_current_user_id)
)->None:
    return service.delete_movie(movie_id)
