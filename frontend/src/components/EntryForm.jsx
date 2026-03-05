import { useState, useEffect } from 'react';
import './EntryForm.css';

export default function EntryForm({ entry, date, onSave, onCancel }) {
  const [clockIn, setClockIn] = useState(entry?.clock_in || '09:00');
  const [clockOut, setClockOut] = useState(entry?.clock_out || '17:00');
  const [note, setNote] = useState(entry?.note || '');
  const [error, setError] = useState('');

  useEffect(() => {
    if (entry) {
      setClockIn(entry.clock_in);
      setClockOut(entry.clock_out);
      setNote(entry.note || '');
    }
  }, [entry]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (clockOut <= clockIn) {
      setError('Out must be after in.');
      return;
    }
    onSave({
      date: entry?.date || date,
      clock_in: clockIn,
      clock_out: clockOut,
      note,
    });
  };

  return (
    <div className="entry-form-overlay" onClick={onCancel}>
      <form className="entry-form" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="entry-form-header">
          <span className="entry-form-title">{entry ? 'EDIT' : 'ADD'} ENTRY</span>
          <span className="entry-form-date">{entry?.date || date}</span>
        </div>

        {error && <div className="entry-form-error">{error}</div>}

        <div className="entry-form-row">
          <label className="entry-form-label">
            <span className="label-text">CLOCK IN</span>
            <input type="time" value={clockIn} onChange={(e) => setClockIn(e.target.value)} required />
          </label>
          <label className="entry-form-label">
            <span className="label-text">CLOCK OUT</span>
            <input type="time" value={clockOut} onChange={(e) => setClockOut(e.target.value)} required />
          </label>
        </div>

        <label className="entry-form-label">
          <span className="label-text">NOTE</span>
          <input type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note..." />
        </label>

        <div className="entry-form-actions">
          <button type="button" className="btn-cancel" onClick={onCancel}>CANCEL</button>
          <button type="submit" className="btn-save">{entry ? 'UPDATE' : 'SAVE'}</button>
        </div>
      </form>
    </div>
  );
}
