import { describe, it, expect } from 'vitest';
import { formatHours, daysInMonth, firstDayOfMonth, isWeekend, monthName } from './dates';

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
