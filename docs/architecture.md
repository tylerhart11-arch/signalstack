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

- `providers/`: live source adapters
- `mappers/`: indicator definitions and series metadata
- `refresh.py`: live-only refresh plus derived-table hydration
- `scheduler.py`: optional background loop for market-hours refresh while the API is running, with exchange-calendar support for holidays and half-days

## Frontend Design

- `src/app/`: route-level pages
- `src/components/layout/`: shell, sidebar, topbar
- `src/components/ui/`: reusable display primitives
- `src/components/overview|regime|feed|thesis/`: feature components
- `src/lib/api.ts`: live-only API client with explicit request errors

The frontend pages are mostly client-rendered so they can surface explicit unavailable states if the live API is not reachable at load time.

## Persistence

PostgreSQL is the primary store for:

- indicator snapshots
- regime history
- anomaly feed items
- saved theses
