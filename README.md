# Stone Paper Scissors

A full-stack, 2-player Stone Paper Scissors game built as a technical assessment. Two
players take turns choosing stone, paper, or scissors across exactly six rounds; the
backend is the single source of truth for game rules, scoring, and the final winner.

## Overview

- Two players enter their names and play a 6-round match on one shared screen.
- Every round's result, running scores, tie count, and the final winner are computed
  and stored entirely on the backend — the frontend only displays what the API returns.
- Every completed (and in-progress) game is persisted in PostgreSQL and viewable later
  from a game history screen, including a full round-by-round breakdown.

## Features

- Stone / paper / scissors round play with backend-authoritative win/lose/tie logic
- Enforced 6-round games, with automatic completion and final-winner calculation
- Game history list, newest first, with a detail view showing all rounds of a game
- Friendly, non-technical error handling for validation errors, 404s, and network failures
- REST API fully decoupled from the React frontend via a documented HTTP contract

## Tech Stack

- **Frontend:** React, Vite, JavaScript, plain `fetch` (no Redux, no Axios)
- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **Production (planned):** AWS EC2, Nginx, Gunicorn

## Architecture

```
stone-paper-scissors/
├── backend/            Django + DRF API (source of truth for game rules)
│   └── games/
│       ├── models.py       Game, Round (schema only)
│       ├── services.py     game engine: win/lose/tie, scoring, 6-round completion
│       ├── serializers.py  request/response shape and input validation
│       ├── views.py        HTTP request/response handling only
│       └── tests.py        model, service, and API tests
└── frontend/            React + Vite single-page app
    └── src/
        ├── services/api.js   the only module that talks to the backend
        └── components/       presentational screens (start, game, history, detail)
```

Responsibilities are kept deliberately separated:

- **Models** define the database schema only.
- **Services** (`games/services.py`) own all game rules — the winner of a round, score
  and tie updates, and when/how a game completes. Nothing else in the backend
  recalculates these.
- **Serializers** validate and shape HTTP input/output; they never contain game rules.
- **Views** handle HTTP concerns and delegate to the service layer.
- The **React frontend** never computes a round or game winner — it sends player
  choices to the API and renders whatever the backend responds with.

## Backend Setup

Requires Python 3.13+ and a running PostgreSQL server.

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows; use `cp` on macOS/Linux — then fill in real values
```

### PostgreSQL setup

Create the local database once (matching whatever you put in `.env`):

```sql
CREATE DATABASE stone_paper_scissors;
```

Then apply migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

## Frontend Setup

Requires Node.js 20+.

```bash
cd frontend
npm install
copy .env.example .env   # Windows; use `cp` on macOS/Linux — then fill in real values
npm run dev
```

The app is available at `http://localhost:5173/`.

## Environment Variables

Both `backend/.env.example` and `frontend/.env.example` document every variable the
app reads. Copy each to `.env` in its respective folder and fill in real values.
`.env` files are gitignored and must never be committed.

**Backend** (`backend/.env`):

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key. Required once `DEBUG=False`. |
| `DEBUG` | `True` for local development, `False` in production. |
| `ALLOWED_HOSTS` | Comma-separated hostnames the backend will serve. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins allowed to call the API. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins trusted for Django admin login (HTTPS only). |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection. |
| `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_*` | HTTPS-only security settings; leave `False` for local HTTP development. |

**Frontend** (`frontend/.env`):

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend API, e.g. `http://127.0.0.1:8000/api`. |

## API Endpoints

| Method | URL | Description |
|---|---|---|
| `POST` | `/api/games/` | Create a new game from two player names |
| `GET` | `/api/games/` | List all games, newest first |
| `GET` | `/api/games/<id>/` | Retrieve one game, including all its rounds |
| `POST` | `/api/games/<id>/rounds/` | Play the next round (`round_number`, `player1_choice`, `player2_choice`) |

## Running Locally

1. Start PostgreSQL.
2. In one terminal: `cd backend && venv\Scripts\activate && python manage.py runserver`
3. In another terminal: `cd frontend && npm run dev`
4. Open `http://localhost:5173/`.

## Testing

**Backend:**

```bash
cd backend
python manage.py test games
python manage.py check
python manage.py check --deploy   # review production-readiness warnings
```

**Frontend:**

```bash
cd frontend
npm run lint
npm run build
```

## Status

- [x] Phase 0 — Project scaffolding
- [x] Phase 1 — Database models (Game, Round)
- [x] Phase 2 — Game engine / service layer
- [x] Phase 3 — REST API
- [x] Phase 4 — End-to-end API verification
- [x] Phase 5 — React frontend
- [ ] AWS deployment
