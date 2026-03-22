# SignalStack

SignalStack is a personal financial analysis platform for top-down market work. It combines:

- a market overview dashboard
- a rules-based macro regime detector
- a curiosity/anomaly feed
- a thesis-to-exposure engine

The repo is organized as a local-first monorepo. Live market and macro APIs are optional; the app will still boot with realistic demo data if they are unavailable.

## Stack

- Frontend: Next.js, React, TypeScript, Tailwind
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- Infra: Docker Compose
- Data: FRED, Yahoo Finance, deterministic demo fallback

## Repo Layout

```text
signalstack/
  docs/      product, architecture, roadmap, data dictionary
  infra/     database bootstrap assets
  frontend/  Next.js app router UI
  backend/   FastAPI API, services, engines, providers, tests
```

## Quick Start

### Option A: Docker Compose

1. Copy [`.env.example`](./.env.example) to `.env`.
2. Run `docker compose up`.
3. Open:
   - Frontend: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`
   - Health: `http://localhost:8000/health`

Notes:

- The first frontend/backend container boot installs dependencies inside the containers.
- Demo data is enabled by default, so the app works even without `FRED_API_KEY`.

### Option B: Run on Host

Prereqs:

- Python 3.12+
- Node 20+
- npm 10+
- PostgreSQL 16+

Backend:

1. Copy [`backend/.env.example`](./backend/.env.example) to `backend/.env`.
2. Install deps: `python -m pip install -r backend/requirements.txt`
3. Start API: `cd backend && uvicorn app.main:app --reload`

Frontend:

1. Copy [`frontend/.env.local.example`](./frontend/.env.local.example) to `frontend/.env.local`.
2. Install deps: `cd frontend && npm install`
3. Start app: `npm run dev`

Database:

- Create a local Postgres database named `signalstack`, or use only the `db` service from Docker Compose.

## API Endpoints

- `GET /health`
- `GET /api/overview`
- `GET /api/regime/current`
- `GET /api/regime/history`
- `GET /api/anomalies`
- `POST /api/thesis/analyze`
- `GET /api/thesis/saved`
- `POST /api/thesis/saved`

## Development Notes

- Business logic lives in backend services and engines, not in route handlers.
- Live data is loaded per series with demo fallback, so one failed provider does not blank the whole app.
- The frontend API layer also falls back to realistic mock responses if the backend is unavailable.
- The regime, anomaly, and thesis engines are intentionally transparent so you can edit the logic directly.

## Testing

From `backend/`:

```bash
pytest
```

From `frontend/`:

```bash
npm run typecheck
```

I could verify backend tests in this environment. I could not run Docker or a Next.js build here because Docker and Node/npm are not installed on this machine.
