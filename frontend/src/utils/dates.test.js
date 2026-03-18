import { describe, it, expect } from 'vitest';
import { formatHours, daysInMonth, firstDayOfMonth, isWeekend, monthName, shortDayName, getWeekNumber, getWeekDates } from './dates';

describe('monthName', () => {
  it('returns the correct month name', () => {
    expect(monthName(1)).toBe('January');
    expect(monthName(12)).toBe('December');
  });

  it('returns empty string for out-of-range', () => {
    expect(monthName(0)).toBe('');
    expect(monthName(13)).toBe('');
  });
});

describe('daysInMonth', () => {
  it('returns 31 for January', () => {
    expect(daysInMonth(2025, 1)).toBe(31);
  });

  it('returns 28 for February in a non-leap year', () => {
    expect(daysInMonth(2025, 2)).toBe(28);
  });

  it('returns 29 for February in a leap year', () => {
    expect(daysInMonth(2024, 2)).toBe(29);
  });
});

describe('isWeekend', () => {
  it('identifies Saturday as weekend', () => {
    expect(isWeekend(2025, 3, 1)).toBe(true); // March 1, 2025 is a Saturday
  });

  it('identifies Monday as weekday', () => {
    expect(isWeekend(2025, 3, 3)).toBe(false); // March 3, 2025 is a Monday
  });
});

describe('formatHours', () => {
  it('formats whole hours', () => {
    expect(formatHours(8)).toBe('8h');
  });

  it('formats hours with minutes', () => {
    expect(formatHours(8.5)).toBe('8h 30m');
  });

  it('formats partial hours correctly', () => {
    expect(formatHours(1.25)).toBe('1h 15m');
  });
});

describe('shortDayName', () => {
  it('returns MON for a Monday', () => {
    expect(shortDayName(2025, 3, 3)).toBe('MON'); // March 3, 2025 is Monday
  });

  it('returns SUN for a Sunday', () => {
    expect(shortDayName(2025, 3, 2)).toBe('SUN');
  });

  it('returns SAT for a Saturday', () => {
    expect(shortDayName(2025, 3, 1)).toBe('SAT');
  });
});

describe('getWeekNumber', () => {
  it('returns correct week number for early January', () => {
    // Jan 6, 2025 is Monday of week 2
    expect(getWeekNumber(2025, 1, 6)).toBe(2);
  });

  it('returns week 1 for first week of year', () => {
    // Dec 30, 2024 is Monday of ISO week 1 of 2025
    // But our function uses the date's own year, so Jan 1, 2025 (Wed) is in week 1
    expect(getWeekNumber(2025, 1, 1)).toBe(1);
  });
});

describe('getWeekDates', () => {
  it('returns 7 dates starting from Monday', () => {
    // March 5, 2025 is a Wednesday
    const dates = getWeekDates(2025, 3, 5);
    expect(dates).toHaveLength(7);
    expect(dates[0].dateStr).toBe('2025-03-03'); // Monday
    expect(dates[6].dateStr).toBe('2025-03-09'); // Sunday
  });

  it('handles cross-month boundaries', () => {
    // March 1, 2025 is Saturday — week starts Feb 24
    const dates = getWeekDates(2025, 3, 1);
    expect(dates[0].dateStr).toBe('2025-02-24'); // Monday in Feb
    expect(dates[0].month).toBe(2);
    expect(dates[6].dateStr).toBe('2025-03-02'); // Sunday in Mar
    expect(dates[6].month).toBe(3);
  });

  it('returns Monday when given a Monday', () => {
    const dates = getWeekDates(2025, 3, 3);
    expect(dates[0].dateStr).toBe('2025-03-03');
  });

  it('returns correct week when given a Sunday', () => {
    const dates = getWeekDates(2025, 3, 9);
    expect(dates[0].dateStr).toBe('2025-03-03'); // Monday of that week
    expect(dates[6].dateStr).toBe('2025-03-09'); // Sunday
  });
});
