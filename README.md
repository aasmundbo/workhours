# PUNCH — Work Hours Tracker

A self-hosted Docker web app for tracking your work hours when your employer doesn't.

## Quick Start

```bash
docker compose up --build
```

Open **http://localhost:8080**

## Features

- **Monthly calendar view** — Click any day to add entries, click entries to edit
- **Easy in/out times** — Clock-in/out uses strict 24-hour `HH:MM` format
- **Stats page** — Weekly breakdown, daily average, on-track indicator for 40h/week
- **Persistent storage** — JSON file on a Docker volume

## Architecture

| Service   | Tech          | Port |
|-----------|---------------|------|
| Backend   | Flask/Python  | 5000 |
| Frontend  | React/Vite    | 3000 |
| Proxy     | Nginx         | 8080 |

## API

- `GET /api/entries?year=2025&month=3` — List entries
- `POST /api/entries` — Create entry
- `PUT /api/entries/:id` — Update entry
- `DELETE /api/entries/:id` — Delete entry
- `GET /api/stats?year=2025&month=3` — Monthly statistics

Time format rules:

- `clock_in` and `clock_out` must be 24-hour `HH:MM` (zero-padded)
- Examples: `08:30`, `17:45`
- Invalid examples: `8:30`, `04:30 PM`

## Testing

After any code change, run the relevant test suite(s) and only consider the work complete when all tests pass.

```bash
cd backend
uv sync
uv run pytest tests/ -v
```

## Data

Hours are stored in `/data/hours.json` in the backend container. Data persists across rebuilds via a host bind mount:

```bash
mkdir -p ~/workhours
```

```yaml
volumes:
  - ${HOME}/workhours:/data
```
