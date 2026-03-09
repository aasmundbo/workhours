import { useState, useEffect } from 'react';
import './TimeInput.css';

/**
 * A 24-hour time input composed of two text fields (HH and MM).
 * Both fields respond to ArrowUp / ArrowDown for increment / decrement,
 * with wrap-around at 23→00 for hours and 59→00 for minutes.
 *
 * Props:
 *   value    – controlled time string "HH:MM" or ""
 *   onChange – called with the new "HH:MM" string whenever both fields are valid
 *   required – marks both fields required for native form validation
 *   id       – optional id applied to the wrapper div
 */
export default function TimeInput({ value, onChange, required, id }) {
  const [hh, setHh] = useState('');
  const [mm, setMm] = useState('');

  useEffect(() => {
    if (value && /^\d{2}:\d{2}$/.test(value)) {
      const [h, m] = value.split(':');
      setHh(h);
      setMm(m);
    } else {
      setHh('');
      setMm('');
    }
  }, [value]);

  const emit = (h, m) => {
    if (h.length === 2 && m.length === 2) {
      onChange(`${h}:${m}`);
    }
  };

  /* ── Hours handlers ── */
  const handleHoursKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const v = String((parseInt(hh || '0', 10) + 1) % 24).padStart(2, '0');
      setHh(v);
      emit(v, mm);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const v = String((parseInt(hh || '0', 10) - 1 + 24) % 24).padStart(2, '0');
      setHh(v);
      emit(v, mm);
    }
  };

  const handleHoursChange = (e) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 2);
    const n = parseInt(raw, 10);
    if (raw === '' || (!isNaN(n) && n <= 23)) {
      setHh(raw);
      if (raw.length === 2) emit(raw, mm);
    }
  };

  const handleHoursBlur = () => {
    if (hh !== '') {
      const v = String(parseInt(hh, 10)).padStart(2, '0');
      setHh(v);
      emit(v, mm);
    }
  };

  /* ── Minutes handlers ── */
  const handleMinutesKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const v = String((parseInt(mm || '0', 10) + 1) % 60).padStart(2, '0');
      setMm(v);
      emit(hh, v);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const v = String((parseInt(mm || '0', 10) - 1 + 60) % 60).padStart(2, '0');
      setMm(v);
      emit(hh, v);
    }
  };

  const handleMinutesChange = (e) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 2);
    const n = parseInt(raw, 10);
    if (raw === '' || (!isNaN(n) && n <= 59)) {
      setMm(raw);
      if (raw.length === 2) emit(hh, raw);
    }
  };

  const handleMinutesBlur = () => {
    if (mm !== '') {
      const v = String(parseInt(mm, 10)).padStart(2, '0');
      setMm(v);
      emit(hh, v);
    }
  };

  return (
    <div className="time-input-24h" id={id}>
      <input
        type="text"
        role="spinbutton"
        aria-label="Hours"
        aria-valuemin={0}
        aria-valuemax={23}
        aria-valuenow={hh !== '' ? parseInt(hh, 10) : undefined}
        inputMode="numeric"
        placeholder="HH"
        maxLength={2}
        value={hh}
        onChange={handleHoursChange}
        onKeyDown={handleHoursKeyDown}
        onBlur={handleHoursBlur}
        required={required}
        className="time-input-field time-input-hours"
      />
      <span className="time-sep" aria-hidden="true">:</span>
      <input
        type="text"
        role="spinbutton"
        aria-label="Minutes"
        aria-valuemin={0}
        aria-valuemax={59}
        aria-valuenow={mm !== '' ? parseInt(mm, 10) : undefined}
        inputMode="numeric"
        placeholder="MM"
        maxLength={2}
        value={mm}
        onChange={handleMinutesChange}
        onKeyDown={handleMinutesKeyDown}
        onBlur={handleMinutesBlur}
        required={required}
        className="time-input-field time-input-minutes"
      />
    </div>
  );
}
