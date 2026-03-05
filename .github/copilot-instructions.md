# Copilot Instructions for This Workhours Repo

## Big picture
- This repo is a self-hosted work-hours tracker with a Flask backend, React/Vite frontend, and Nginx reverse proxy.
- Primary user flow: add/edit/delete day entries in monthly calendar, then review monthly/weekly stats.
- Keep changes focused on the existing product scope (timesheet + stats), not feature expansion.

## Architecture at a glance
- `backend/` is a Flask API service (`app.py`) using blueprints in `backend/routes/`.
- `frontend/` is a React app (Vite) with pages in `frontend/src/pages/` and shared components in `frontend/src/components/`.
- `docker-compose.yml` runs backend (`:5000`), frontend (`:3000`), and Nginx (`:8080`).
- Nginx proxies `/api/*` to backend and serves the frontend app.

## Core workflows
- Full stack (recommended):
  - `docker compose up --build`
  - Open `http://localhost:8080`
- Backend tests:
  - `cd backend`
  - `pip install -r requirements.txt`
  - `pytest tests/ -v`
- Frontend local dev:
  - `cd frontend`
  - `npm install`
  - `npm run dev`

## Data and API conventions
- Entry payload shape is snake_case: `date`, `clock_in`, `clock_out`, `note`, computed `hours`, plus `id`.
- Date/time formats are strict:
  - date: `YYYY-MM-DD`
  - time: `HH:MM` (24-hour)
- Validation and hour computation should stay centralized in backend model helpers (avoid duplicating logic in routes).
- Stats endpoint behavior should remain deterministic for month/year filtering and weekly aggregation.

## Backend editing conventions
- Keep route handlers thin: parse request, validate, delegate to model/storage helpers, return JSON.
- Preserve blueprint structure and endpoint paths (`/api/entries`, `/api/stats`).
- Keep storage changes backward-compatible with tests under `backend/tests/`.
- Prefer explicit, readable Python over abstractions.

## Frontend editing conventions
- Keep UI structure page-driven (`MonthView`, `Stats`) with small reusable components (`EntryForm`, `MonthNav`).
- Use existing API client in `frontend/src/api/client.js` for HTTP calls; avoid ad hoc fetch logic in pages.
- Preserve field naming consistency with backend (`clock_in` / `clock_out` etc).
- Keep styling within existing CSS files and current visual language.

## Testing and validation expectations
- For backend logic/API changes, update or add focused tests in `backend/tests/`.
- Prefer minimal, targeted test additions near changed behavior.
- If README commands or behavior changes, keep `README.md` aligned.

## Scope guardrails
- Do not add unrelated infrastructure, frameworks, or large refactors.
- Avoid changing API contracts unless explicitly requested.
- Prefer minimal, surgical edits that keep the Docker workflow intact.

## Agent checklist before finishing
- Did API field names remain consistent across backend + frontend?
- Did changed backend behavior pass `pytest tests/ -v`?
- Did Docker/local run instructions remain accurate in `README.md`?
- Are changes limited to the requested scope?
