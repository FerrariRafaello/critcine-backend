# Critcine API

A social movie review platform built with FastAPI. Users can create accounts, write reviews, like each other's posts, follow other users, build a watchlist, and browse a personalised feed powered by The Movie Database (TMDB).

---

## Features

- **Authentication** — JWT-based login with token versioning (new login invalidates all previous sessions)
- **User profiles** — name, bio, pronouns, favourite genres, avatar/cover image, CPF validation
- **Reviews** — rate movies 0–10, leave a comment, like reviews
- **Feed** — global review feed with sort (newest / oldest / popular), search by user or movie, and a *Following only* filter
- **Watchlist** — track movies as *want to watch*, *watching*, *watched*, or *dropped*
- **Follow system** — follow / unfollow users, see their follower/following counts
- **TMDB integration** — search, trending, now playing, top rated, discover by genre, streaming providers, trailers, cast

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| DB driver | psycopg3 + psycopg-pool |
| Migrations | Alembic |
| Auth | PyJWT (HS256) |
| Password hashing | passlib / bcrypt |
| Validation | Pydantic v2 |
| Rate limiting | slowapi |
| HTTP client | httpx |
| Logging | loguru (JSON, stdout) |
| Containerisation | Docker + Docker Compose |
| Deployment | Railway |

---

## Project Structure

```
critcine-backend/
├── app/
│   ├── auth/          # login, JWT creation and validation
│   ├── core/          # config, DB pools, brute-force, sanitisation, validators
│   ├── follows/       # follow/unfollow, followers/following lists
│   ├── movies/        # local movie CRUD
│   ├── reviews/       # reviews, likes, feed
│   ├── tmdb/          # TMDB API client and endpoints
│   ├── users/         # user CRUD and profiles
│   ├── watchlist/     # personal watchlist
│   └── main.py        # app setup, middleware, exception handlers
├── migrations/        # Alembic migration scripts
├── tests/             # pytest test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16
- A [TMDB API key](https://www.themoviedb.org/settings/api)

### Local setup

```bash
# 1. Clone and enter the project
git clone https://github.com/FerrariRafaello/critcine-backend.git
cd critcine-backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file (see Environment Variables section below)
cp .env.example .env

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### Docker setup

```bash
# Build and start the API + PostgreSQL
docker-compose up -d

# Run migrations against the running container
docker-compose exec api alembic upgrade head
```

---

## Environment Variables

Create a `.env` file in the project root. **Never commit this file.**

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/critcine` |
| `JWT_SECRET` | Yes | Long random string used to sign tokens |
| `TMDB_API_KEY` | Yes | API key from themoviedb.org |
| `JWT_ALGORITHM` | No | Defaults to `HS256` |
| `JWT_EXPIRE_MINUTES` | No | Token lifetime in minutes, defaults to `60` |

---

## API Endpoints

All endpoints (except `POST /v1/users` and `POST /v1/auth/login`) require a Bearer token in the `Authorization` header.

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/auth/login` | Login and receive a JWT |

### Users

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/users` | Register a new account |
| `GET` | `/v1/users/me` | Get the current user's profile |
| `GET` | `/v1/users` | List all users |
| `GET` | `/v1/users/{user_id}` | Get a user by ID |
| `PUT` | `/v1/users/{user_id}` | Full profile update (own profile only) |
| `PATCH` | `/v1/users/{user_id}` | Partial profile update (own profile only) |
| `DELETE` | `/v1/users/{user_id}` | Delete account (own account only) |

### Follows

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/users/{user_id}/follow` | Follow a user |
| `DELETE` | `/v1/users/{user_id}/follow` | Unfollow a user |
| `GET` | `/v1/users/{user_id}/followers` | List a user's followers |
| `GET` | `/v1/users/{user_id}/following` | List users a user follows |

### Reviews

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/reviews` | Create a review |
| `GET` | `/v1/reviews/feed` | Global feed (sort, search, following filter) |
| `GET` | `/v1/reviews/movie/{tmdb_movie_id}` | All reviews for a movie |
| `GET` | `/v1/reviews/user/{user_id}` | All reviews by a user |
| `PATCH` | `/v1/reviews/{review_id}` | Update a review (author only) |
| `DELETE` | `/v1/reviews/{review_id}` | Delete a review (author only) |
| `POST` | `/v1/reviews/{review_id}/like` | Like a review |

**Feed query params:** `sort` (newest/oldest/popular), `search_user`, `search_movie`, `following_only`, `limit`, `offset`

### Watchlist

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/watchlist` | Add a movie to the watchlist |
| `GET` | `/v1/watchlist` | Get the current user's watchlist |
| `PATCH` | `/v1/watchlist/{item_id}` | Update watchlist item status |
| `DELETE` | `/v1/watchlist/{item_id}` | Remove from watchlist |

### Movies (local catalogue)

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/movies` | Create a movie entry |
| `GET` | `/v1/movies` | List movies |
| `GET` | `/v1/movies/{movie_id}` | Get a movie by ID |
| `PUT` | `/v1/movies/{movie_id}` | Full movie update |
| `PATCH` | `/v1/movies/{movie_id}` | Partial movie update |
| `DELETE` | `/v1/movies/{movie_id}` | Delete a movie |

### TMDB

| Method | Path | Description |
|---|---|---|
| `GET` | `/v1/tmdb/search` | Search movies by title |
| `GET` | `/v1/tmdb/trending` | Weekly trending movies |
| `GET` | `/v1/tmdb/now-playing` | Currently in cinemas |
| `GET` | `/v1/tmdb/top-rated` | All-time top rated |
| `GET` | `/v1/tmdb/top10-today` | Daily top 10 in Brazil |
| `GET` | `/v1/tmdb/discover` | Discover by genre |
| `GET` | `/v1/tmdb/for-you` | Personalised by genre list |
| `GET` | `/v1/tmdb/classics` | Pre-1990 classics |
| `GET` | `/v1/tmdb/animation` | Animation movies |
| `GET` | `/v1/tmdb/providers` | Available streaming providers |
| `GET` | `/v1/tmdb/providers/{provider_id}/movies` | Movies by streaming service |
| `GET` | `/v1/tmdb/movies/{movie_id}` | Movie detail |
| `GET` | `/v1/tmdb/movies/{movie_id}/credits` | Cast and crew |
| `GET` | `/v1/tmdb/movies/{movie_id}/videos` | Trailers and clips |
| `GET` | `/v1/tmdb/movies/{movie_id}/providers` | Where to watch |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |

---

## Security

| Measure | Detail |
|---|---|
| JWT with token versioning | Each login increments `token_version` in the DB, invalidating all previous tokens |
| Brute-force protection | IP locked for 15 minutes after 5 failed login attempts in 10 minutes |
| Registration rate limit | Max 2 accounts per IP per 24 hours |
| Rate limiting (slowapi) | Per-endpoint limits (5–30 req/min on write paths) |
| Password policy | Min 8 chars, requires uppercase, lowercase, and a digit |
| Input sanitisation | HTML stripped from all free-text fields before storage (XSS prevention) |
| CPF validation | Algorithmic check on the Brazilian CPF number (digit verification) |
| Ownership checks | Users can only modify or delete their own resources |
| Security headers | HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy |
| Honeypot middleware | Common scanner paths (`.env`, `wp-admin`, etc.) are logged and return 404 |
| Payload size limit | Requests larger than 1 MB are rejected before body parsing |
| Request ID | Every request gets a UUID in `X-Request-ID` for log correlation |
| CORS | Restricted to known frontend origins |
| Docker network isolation | PostgreSQL is only reachable from within the internal Docker network |
| HTTP timeouts | All outbound TMDB requests have a 10-second timeout to prevent thread hang |

---

## Testing

```bash
# Make sure the test database exists and migrations are up to date
DATABASE_URL=postgresql://user:pass@localhost:5432/critcine_test \
  python -m alembic upgrade head

# Run the full test suite
TESTING=1 pytest -v
```

The `TESTING=1` flag disables brute-force lockouts, IP registration limits, token version checks, and rate limits so fixtures don't interfere with each other.

---

## CPF Validation

The CPF (Cadastro de Pessoas Físicas) is the Brazilian individual taxpayer number. This project implements the full digit-verification algorithm from scratch. The field is **optional** — users without a CPF can still register.

---

## License

MIT
