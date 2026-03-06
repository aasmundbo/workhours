# PUNCH — Work Hours Tracker

A self-hosted Docker web app for tracking your work hours when your employer doesn't.

## Quick Start

### 1. Create the data directory

Hours are stored in `/data/hours.json` in the backend container. Data persists across rebuilds via a host bind mount:

```bash
mkdir -p ~/workhours
```

### 2. Configure your work schedule

Copy the default config and edit it to match your contract:

```bash
cp .env.default .env
```

Open `.env` and set your values:

| Variable | Default | Description |
|---|---|---|
| `WORK_HOURS_PER_WEEK` | `40` | Total contracted hours per week |
| `WORK_DAYS_PER_WEEK` | `5` | Working days per week (Mon onwards — `5`=Mon–Fri, `4`=Mon–Thu, etc.) |

> `.env` is git-ignored. Never commit it.

### 3. Start the app

```bash
docker compose up --build
```

Open **http://localhost:8080**

## Features

- **Monthly calendar view** — Click any day to add entries, click entries to edit
- **Easy in/out times** — Clock-in/out uses strict 24-hour `HH:MM` format
- **Stats page** — Weekly breakdown, daily average, and pace indicators showing whether you are ahead or behind for the current week and current month
- **Off days** — Mark individual days as no-work (public holidays, leave). Off days are excluded from the expected hours target; any hours actually logged on those days still count toward your total
- **Configurable schedule** — Set your contracted hours and working days per week via environment variables
- **Persistent storage** — JSON file on a Docker volume

## Architecture

| Service   | Tech          | Port |
|-----------|---------------|------|
| Backend   | Flask/Python  | 5000 |
| Frontend  | React/Vite    | 3000 |
| Proxy     | Nginx         | 8080 |

## API

### Entries

- `GET /api/entries?year=2025&month=3` — List entries for a month
- `POST /api/entries` — Create entry (`clock_out` optional for open/punched-in entries)
- `PUT /api/entries/:id` — Update entry
- `DELETE /api/entries/:id` — Delete entry

### Off days

- `GET /api/off-days` — List all off days
- `GET /api/off-days?year=2025&month=3` — List off days for a month
- `POST /api/off-days` — Mark a day as off (`{"date": "YYYY-MM-DD"}`). Idempotent.
- `DELETE /api/off-days/2025-03-17` — Remove an off day

### Stats

- `GET /api/stats?year=2025&month=3` — Monthly statistics

Key response fields:

| Field | Description |
|---|---|
| `total_hours` | Hours logged with both clock-in and clock-out |
| `target_hours` | Contracted hours for the month (adjusted for off days) |
| `expected_so_far` | Target pro-rated to the last completed workday |
| `difference` | `total_hours − expected_so_far` (positive = ahead) |
| `on_track` | `true` when `difference >= 0` |
| `week_difference` | Ahead/behind for the current week |
| `week_target_so_far` | Week target pro-rated to the last completed workday |
| `elapsed_workdays` | Workdays counted so far (off days excluded) |
| `off_days` | List of `YYYY-MM-DD` strings for the queried month |
| `hours_per_day` | Derived from schedule (`hours_per_week / work_days_per_week`) |
| `weekly` | Per-week breakdown with `week`, `hours`, `target`, `difference` |

### Time format rules

- `clock_in` and `clock_out` must be 24-hour `HH:MM` (zero-padded)
- Examples: `08:30`, `17:45`
- Invalid: `8:30`, `04:30 PM`

## Testing

After any code change, run the relevant test suite(s) and only consider the work complete when all tests pass.

```bash
cd backend
uv sync
uv run pytest tests/ -v
```
