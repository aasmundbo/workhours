import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TimeInput from './TimeInput';

describe('TimeInput', () => {
  it('renders hours and minutes from a 24h value', () => {
    render(<TimeInput value="14:30" onChange={() => {}} />);
    expect(screen.getByRole('spinbutton', { name: /hours/i })).toHaveValue('14');
    expect(screen.getByRole('spinbutton', { name: /minutes/i })).toHaveValue('30');
  });

  it('renders leading-zero hours correctly', () => {
    render(<TimeInput value="08:05" onChange={() => {}} />);
    expect(screen.getByRole('spinbutton', { name: /hours/i })).toHaveValue('08');
    expect(screen.getByRole('spinbutton', { name: /minutes/i })).toHaveValue('05');
  });

  it('renders empty fields when no value provided', () => {
    render(<TimeInput value="" onChange={() => {}} />);
    expect(screen.getByRole('spinbutton', { name: /hours/i })).toHaveValue('');
    expect(screen.getByRole('spinbutton', { name: /minutes/i })).toHaveValue('');
  });

  it('calls onChange with new HH:MM when hours are incremented via ArrowUp', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="08:30" onChange={onChange} />);
    const hoursInput = screen.getByRole('spinbutton', { name: /hours/i });
    await user.click(hoursInput);
    await user.keyboard('{ArrowUp}');
    expect(onChange).toHaveBeenCalledWith('09:30');
  });

  it('calls onChange with new HH:MM when hours are decremented via ArrowDown', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="08:30" onChange={onChange} />);
    const hoursInput = screen.getByRole('spinbutton', { name: /hours/i });
    await user.click(hoursInput);
    await user.keyboard('{ArrowDown}');
    expect(onChange).toHaveBeenCalledWith('07:30');
  });

  it('wraps hours from 23 to 00 on ArrowUp', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="23:00" onChange={onChange} />);
    const hoursInput = screen.getByRole('spinbutton', { name: /hours/i });
    await user.click(hoursInput);
    await user.keyboard('{ArrowUp}');
    expect(onChange).toHaveBeenCalledWith('00:00');
  });

  it('wraps hours from 00 to 23 on ArrowDown', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="00:00" onChange={onChange} />);
    const hoursInput = screen.getByRole('spinbutton', { name: /hours/i });
    await user.click(hoursInput);
    await user.keyboard('{ArrowDown}');
    expect(onChange).toHaveBeenCalledWith('23:00');
  });

  it('calls onChange with new HH:MM when minutes are incremented via ArrowUp', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="08:30" onChange={onChange} />);
    const minutesInput = screen.getByRole('spinbutton', { name: /minutes/i });
    await user.click(minutesInput);
    await user.keyboard('{ArrowUp}');
    expect(onChange).toHaveBeenCalledWith('08:31');
  });

  it('wraps minutes from 59 to 00 on ArrowUp', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="08:59" onChange={onChange} />);
    const minutesInput = screen.getByRole('spinbutton', { name: /minutes/i });
    await user.click(minutesInput);
    await user.keyboard('{ArrowUp}');
    expect(onChange).toHaveBeenCalledWith('08:00');
  });

  it('wraps minutes from 00 to 59 on ArrowDown', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<TimeInput value="08:00" onChange={onChange} />);
    const minutesInput = screen.getByRole('spinbutton', { name: /minutes/i });
    await user.click(minutesInput);
    await user.keyboard('{ArrowDown}');
    expect(onChange).toHaveBeenCalledWith('08:59');
  });
});
