import { useState, useEffect } from 'react';
import './EntryForm.css';

function getNow() {
  const d = new Date();
  return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
}

export default function EntryForm({ entry, date, onSave, onCancel, onDelete }) {
  const [clockIn, setClockIn] = useState(entry?.clock_in || '08:00');
  const [clockOut, setClockOut] = useState(entry ? (entry.clock_out || '') : '');
  const [note, setNote] = useState(entry?.note || '');
  const [error, setError] = useState('');

  useEffect(() => {
    if (entry) {
      setClockIn(entry.clock_in);
      setClockOut(entry.clock_out || '');
      setNote(entry.note || '');
    }
  }, [entry]);

  const title = entry ? 'EDIT' : 'ADD';

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (clockOut && clockOut <= clockIn) {
      setError('Clock out must be after clock in.');
      return;
    }
    onSave({
      date: entry?.date || date,
      clock_in: clockIn,
      clock_out: clockOut || null,
      note,
    });
  };

  return (
    <div className="entry-form-overlay" onClick={onCancel}>
      <form className="entry-form" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="entry-form-header">
          <span className="entry-form-title">{title} ENTRY</span>
          <span className="entry-form-date">{entry?.date || date}</span>
        </div>

        {error && <div className="entry-form-error">{error}</div>}

        <div className="entry-form-row">
          <div className="entry-form-label">
            <span className="label-text">CLOCK IN</span>
            <div className="time-input-group">
              <input type="time" value={clockIn} onChange={(e) => setClockIn(e.target.value)} required />
              <button type="button" className="btn-now" onClick={() => setClockIn(getNow())}>NOW</button>
            </div>
          </div>
          <div className="entry-form-label">
            <span className="label-text">CLOCK OUT <span className="label-optional">(OPTIONAL)</span></span>
            <div className="time-input-group">
              <input type="time" value={clockOut} onChange={(e) => setClockOut(e.target.value)} />
              <button type="button" className="btn-now" onClick={() => setClockOut(getNow())}>NOW</button>
            </div>
          </div>
        </div>

        <div className="entry-form-label">
          <span className="label-text">NOTE</span>
          <input type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note..." />
        </div>

        <div className="entry-form-actions">
          {entry && onDelete && (
            <button type="button" className="btn-delete" onClick={() => onDelete(entry)}>DELETE</button>
          )}
          <button type="button" className="btn-cancel" onClick={onCancel}>CANCEL</button>
          <button type="submit" className="btn-save">SAVE</button>
        </div>
      </form>
    </div>
  );
}
