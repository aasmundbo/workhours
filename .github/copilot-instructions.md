# Copilot Instructions for This Workhours Repo

## Big picture
- This repo is a self-hosted work-hours tracker with a Flask backend, React/Vite frontend, and Nginx reverse proxy.
- Primary user flows: punch in/out from the today panel on the monthly calendar; edit or delete any entry; review monthly/weekly stats.
- Keep changes focused on the existing product scope (timesheet + stats), not feature expansion.

## Architecture at a glance
- `backend/` is a Flask API service (`app.py`) using blueprints in `backend/routes/`.
- `frontend/` is a React app (Vite) with pages in `frontend/src/pages/` and shared components in `frontend/src/components/`.
- `docker-compose.yml` runs backend (`:5000`), frontend (`:3000`), and Nginx (`:8080`).
- Nginx proxies `/api/*` to backend and serves the frontend app.
- Entry data is stored in `~/workhours/hours.json` on the host via a bind mount to `/data` in the backend container.

## Core workflows
- Full stack (recommended):
  - `mkdir -p ~/workhours`
  - `docker compose up --build`
  - Open `http://localhost:8080`
- Backend tests:
  - `cd backend`
  - `uv run pytest tests/ -v`
- Frontend local dev:
  - `cd frontend`
  - `npm install`
  - `npm run dev`

## Data and API conventions
- Entry payload shape is snake_case: `id`, `date`, `clock_in`, `clock_out`, `hours`, `note`.
- `clock_out` and `hours` are **nullable** — omitted or `null` for open (punched-in) entries.
- Date/time formats are strict:
  - date: `YYYY-MM-DD`
  - time: `HH:MM` (24-hour, zero-padded — `"8:30"` is invalid)
- Validation and hour computation stay centralized in `backend/models.py`; do not duplicate in routes.
- Stats endpoint behavior must remain deterministic for month/year filtering and weekly aggregation.
- Open entries (no clock-out) do not contribute to `total_hours` in stats.

## Punch-in / punch-out flow
- **Punch in**: POST `/api/entries` with `{ date, clock_in }` — `clock_out` omitted. Returns an open entry.
- **Punch out**: PUT `/api/entries/:id` with `{ clock_out }` only — the route fetches the stored `clock_in` via `get_entry()`, calls `complete_entry()` in models, and persists the result.
- **Full edit**: PUT `/api/entries/:id` with both `clock_in` and `clock_out` — hours are recomputed.
- Model helpers to use: `is_open(entry)`, `complete_entry(entry, clock_out)`, `create_entry(date, clock_in, clock_out=None)`.
- Storage helpers: `load_entries()`, `save_entries()`, `add_entry()`, `update_entry()`, `delete_entry()`, `get_entry(id)`.
- Storage resolves the data file path at call time from `DEFAULT_PATH` (env var `DATA_FILE`, default `/data/hours.json`), so tests can monkeypatch `storage.DEFAULT_PATH`.

## Backend editing conventions
- Keep route handlers thin: parse request, validate, delegate to model/storage helpers, return JSON.
- Preserve blueprint structure and endpoint paths (`/api/entries`, `/api/stats`).
- Keep storage changes backward-compatible with tests under `backend/tests/`.
- Prefer explicit, readable Python over abstractions.
- Backend Docker image installs deps into system Python via `uv pip install --system` (no virtualenv in container).

## Frontend editing conventions
- Keep UI structure page-driven (`MonthView`, `Stats`) with small reusable components (`EntryForm`, `MonthNav`).
- `MonthView` owns the today punch panel (PUNCH IN / PUNCH OUT buttons) and passes `onDelete` to `EntryForm`.
- `EntryForm` accepts `entry`, `date`, `onSave`, `onCancel`, and `onDelete` props. `clock_out` is optional; the form shows a DELETE button when `entry` and `onDelete` are both provided.
- Use existing API client in `frontend/src/api/client.js` for all HTTP calls; no ad hoc fetch logic in pages.
- Preserve field naming consistency with backend (`clock_in` / `clock_out` etc).
- Keep styling within existing CSS files and current visual language.

## Testing and validation expectations
- For backend logic/API changes, update or add focused tests in `backend/tests/`.
- Write failing tests first, then implement, then confirm all tests pass.
- After any code change, run the relevant test suite(s) and only consider work complete when all tests pass.
- If README commands or behavior changes, keep `README.md` aligned.

## Scope guardrails
- Do not add unrelated infrastructure, frameworks, or large refactors.
- Avoid changing API contracts unless explicitly requested.
- Prefer minimal, surgical edits that keep the Docker workflow intact.

## Agent checklist before finishing
- Did API field names remain consistent across backend + frontend?
- Are `clock_out` and `hours` handled as nullable everywhere they're touched?
- Did changed backend behavior pass `uv run pytest tests/ -v` with all tests passing?
- Did Docker/local run instructions remain accurate in `README.md`?
- Are changes limited to the requested scope?
