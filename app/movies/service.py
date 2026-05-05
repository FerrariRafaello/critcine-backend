# _ IMPORTS
from app.core.database_movies import MovieDB
from app.core.exceptions import DuplicateEntryError
from app.movies.schemas import CreateMovie, MovieUpdate, MoviePatch, MovieOut


# _ Service Class
class MovieService:
    def __init__(self, db: MovieDB)->None:
        self.db = db

    def create_movie(self, payload:CreateMovie)->MovieOut:
        try:
            movie_id=self.db.create_movie(
                name=payload.name,
                year=payload.year,
                rating=payload.rating,
            )
            return self.get_movie(movie_id)
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

    def list_movies(self, limit:int, offset:int)-> list[MovieOut]:
        rows=self.db.get_movies(limit=limit, offset=offset)

        return [
            MovieOut(
                id=row["id"],
                name=row["name"],
                year=row["year"],
                rating=row["rating"]
            )for row in rows
        ]

    def get_movie(self, movie_id:int)->MovieOut:
        row = self.db.get_movie_by_id(movie_id)
        if row is None:
            raise LookupError("Movie not found")

        return MovieOut(
            id=row["id"],
            name=row["name"],
            year=row["year"],
            rating=row["rating"]
        )

    def update_movie(
            self,
            movie_id:int,
            payload:MovieUpdate
    ) -> MovieOut:
        current = self.db.get_movie_by_id(movie_id)
        if current is None:
            raise LookupError("Movie not found")

        try:
            updated = self.db.update_movie(
                movie_id=movie_id,
                name=payload.name,
                year=payload.year,
                rating=payload.rating
            )
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

        if not updated:
            raise LookupError("Movie not found")

        return self.get_movie(movie_id)

    def patch_movie(self, movie_id:int, payload:MoviePatch)-> MovieOut:
        current = self.db.get_movie_by_id(movie_id)
        if current is None:
            raise LookupError("Movie not found")

        try:
            updated=self.db.patch_movie(
                movie_id=movie_id,
                name=payload.name,
                year=payload.year,
                rating=payload.rating
            )
        except DuplicateEntryError as exc:
            raise ValueError(str(exc))

        if not updated:
            raise LookupError("Movie not found")

        return self.get_movie(movie_id)

    def delete_movie(self, movie_id:int)-> None:
        deleted=self.db.delete_movie(movie_id)
        if not deleted:
            raise LookupError("Movie not found")
