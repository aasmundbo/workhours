# Week View Implementation Plan

## Goal
Create a mobile-friendly week view where each day is a vertical card showing entries with notes visible inline (no hover/click needed). Replace the 7-column month grid with a scrollable list of 7 day cards.

## Architecture Decision
Add WeekView as a **new route** (`/week`) alongside the existing MonthView (`/`). This preserves the month view for desktop users while giving mobile users a better experience.

## Changes

### 1. Add week utilities to `dates.js`
- `getWeekDates(year, month, day)` — returns array of 7 date objects `{year, month, day, dateStr}` for the ISO week containing the given date
- `getWeekNumber(year, month, day)` — returns ISO week number
- `shortDayName(dateStr)` — returns 3-letter day name (MON, TUE, etc.)

### 2. Create `WeekNav.jsx` + `WeekNav.css`
- Prev/Next week buttons
- Shows "WEEK 12 · MAR 2026" style label
- "TODAY" button to jump to current week

### 3. Create `WeekView.jsx` + `WeekView.css`
- Vertical stack of day cards (one per day, Mon–Sun)
- Each day card shows:
  - Day name + date number + day hours total
  - Off-day indicator + toggle button
  - Each entry as a row: time range, note text shown inline, edit/delete actions
  - Tap empty area to add entry
- Punch panel at top (same as MonthView, reuse logic)
- Weekly hours total summary
- Fetches entries for the month(s) the week spans (may cross month boundary)

### 4. Update `App.jsx` routing
- Add `/week` route pointing to WeekView
- Add "WEEK" nav link in header

### 5. Add tests
- `dates.test.js` — tests for `getWeekDates`, `getWeekNumber`, `shortDayName`
- `WeekView.test.jsx` — render tests: displays 7 days, shows entries with notes inline, handles cross-month weeks

### 6. Run all tests and verify
