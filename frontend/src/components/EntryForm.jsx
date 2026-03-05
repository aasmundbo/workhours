import { useState, useEffect } from 'react';
import './EntryForm.css';

export default function EntryForm({ entry, date, onSave, onCancel, onDelete }) {
  // For open entries (punch-in only), default clock_out to empty
  const [clockIn, setClockIn] = useState(entry?.clock_in || '08:00');
  const [clockOut, setClockOut] = useState(entry ? (entry.clock_out || '') : '16:00');
  const [note, setNote] = useState(entry?.note || '');
  const [error, setError] = useState('');

  useEffect(() => {
    if (entry) {
      setClockIn(entry.clock_in);
      setClockOut(entry.clock_out || '');
      setNote(entry.note || '');
    }
  }, [entry]);

  const isOpenEntry = entry && !entry.clock_out;
  const title = entry ? (isOpenEntry ? 'PUNCH OUT' : 'EDIT') : 'ADD';
  const saveLabel = entry ? (isOpenEntry ? 'PUNCH OUT' : 'UPDATE') : 'SAVE';

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (clockOut && clockOut <= clockIn) {
      setError('Out must be after in.');
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
          <label className="entry-form-label">
            <span className="label-text">CLOCK IN</span>
            <input type="time" value={clockIn} onChange={(e) => setClockIn(e.target.value)} required />
          </label>
          <label className="entry-form-label">
            <span className="label-text">CLOCK OUT{!isOpenEntry && !entry ? '' : ' (OPTIONAL)'}</span>
            <input type="time" value={clockOut} onChange={(e) => setClockOut(e.target.value)} />
          </label>
        </div>

        <label className="entry-form-label">
          <span className="label-text">NOTE</span>
          <input type="text" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note..." />
        </label>

        <div className="entry-form-actions">
          {entry && onDelete && (
            <button type="button" className="btn-delete" onClick={() => onDelete(entry)}>DELETE</button>
          )}
          <button type="button" className="btn-cancel" onClick={onCancel}>CANCEL</button>
          <button type="submit" className="btn-save">{saveLabel}</button>
        </div>
      </form>
    </div>
  );
}
