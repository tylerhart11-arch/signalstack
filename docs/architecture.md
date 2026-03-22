# Architecture

## Monorepo Shape

- `frontend/`: Next.js application and UI system
- `backend/`: FastAPI API, persistence, business logic, data refresh
- `infra/`: development database bootstrap assets
- `docs/`: product and implementation documentation

## Backend Design

### Route handlers

Route files in `backend/app/api/routes/` are intentionally thin. They only:

- validate request/response shapes
- open a database session
- delegate to services

### Services

Services coordinate application workflows:

- `overview_service.py`: loads normalized indicator state for the UI
- `regime_service.py`: retrieves current regime output and stored history
- `anomaly_service.py`: returns ranked anomaly items
- `thesis_service.py`: runs thesis analysis and persistence

### Engines

Engines contain the decision logic and can evolve independently from the API:

- `regime_engine.py`: pillar scoring and regime classification
- `anomaly_engine.py`: anomaly rules and ranking logic
- `thesis_engine.py`: taxonomy-based thesis translation

### Data layer

- `providers/`: live source adapters and deterministic demo data
- `mappers/`: indicator definitions and series metadata
- `refresh.py`: blended live/demo refresh plus derived-table hydration

## Frontend Design

- `src/app/`: route-level pages
- `src/components/layout/`: shell, sidebar, topbar
- `src/components/ui/`: reusable display primitives
- `src/components/overview|regime|feed|thesis/`: feature components
- `src/lib/api.ts`: API client with resilient fallback mocks

The frontend pages are mostly client-rendered so they can degrade gracefully if the API is not available at load time.

## Persistence

PostgreSQL is the primary store for:

- indicator snapshots
- regime history
- anomaly feed items
- saved theses

The frontend also uses local storage as a fallback for saved theses if the backend is unavailable.
