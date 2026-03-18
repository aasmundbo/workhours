import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import WeekView from './WeekView';

vi.mock('../api/client', () => ({
  getEntries: vi.fn().mockResolvedValue([]),
  getOffDays: vi.fn().mockResolvedValue([]),
  createEntry: vi.fn().mockResolvedValue({}),
  updateEntry: vi.fn().mockResolvedValue({}),
  deleteEntry: vi.fn().mockResolvedValue({}),
  addOffDay: vi.fn().mockResolvedValue({}),
  removeOffDay: vi.fn().mockResolvedValue({}),
}));

describe('WeekView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders 7 day cards', async () => {
    render(<WeekView />);
    const dayNames = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
    for (const name of dayNames) {
      expect(screen.getByText(name)).toBeInTheDocument();
    }
  });

  it('renders weekly total summary', () => {
    render(<WeekView />);
    expect(screen.getByText('TOTAL')).toBeInTheDocument();
    expect(screen.getByText('this week')).toBeInTheDocument();
  });

  it('renders week navigation', () => {
    render(<WeekView />);
    expect(screen.getByText(/WEEK \d+/)).toBeInTheDocument();
    expect(screen.getByText('TODAY')).toBeInTheDocument();
    expect(screen.getByText('◂ PREV')).toBeInTheDocument();
    expect(screen.getByText('NEXT ▸')).toBeInTheDocument();
  });

  it('shows entries with notes inline', async () => {
    const { getEntries } = await import('../api/client');
    const today = new Date();
    const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    getEntries.mockResolvedValueOnce([
      { id: '1', date: dateStr, clock_in: '08:00', clock_out: '12:00', hours: 4, note: 'Morning work session' },
    ]);

    render(<WeekView />);

    const noteEl = await screen.findByText('Morning work session');
    expect(noteEl).toBeInTheDocument();
    expect(noteEl).toBeVisible();
  });

  it('shows punch panel for current week', () => {
    render(<WeekView />);
    expect(screen.getByText('NOT PUNCHED IN')).toBeInTheDocument();
    expect(screen.getByText('PUNCH IN')).toBeInTheDocument();
  });

  it('shows empty state prompts', async () => {
    render(<WeekView />);
    const emptyPrompts = await screen.findAllByText('tap to add entry');
    expect(emptyPrompts.length).toBeGreaterThan(0);
  });
});
