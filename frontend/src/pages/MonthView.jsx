import { useState, useEffect, useCallback } from 'react';
import MonthNav from '../components/MonthNav';
import EntryForm from '../components/EntryForm';
import { getEntries, createEntry, updateEntry, deleteEntry, getOffDays, addOffDay, removeOffDay } from '../api/client';
import { currentYearMonth, daysInMonth, firstDayOfMonth, isWeekend, formatHours } from '../utils/dates';
import './MonthView.css';

export default function MonthView() {
  const { year: initY, month: initM } = currentYearMonth();
  const [year, setYear] = useState(initY);
  const [month, setMonth] = useState(initM);
  const [entries, setEntries] = useState([]);
  const [offDays, setOffDays] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editEntry, setEditEntry] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [data, offs] = await Promise.all([
        getEntries(year, month),
        getOffDays(year, month),
      ]);
      setEntries(data);
      setOffDays(new Set(offs));
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [year, month]);

  useEffect(() => { load(); }, [load]);

  const handleMonthChange = (y, m) => { setYear(y); setMonth(m); };

  const handleDayClick = (dateStr) => {
    setSelectedDate(dateStr);
    setEditEntry(null);
    setShowForm(true);
  };

  const handleEditClick = (entry, e) => {
    e.stopPropagation();
    setEditEntry(entry);
    setSelectedDate(null);
    setShowForm(true);
  };

  const handleDeleteClick = async (entry, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this entry?')) return;
    await deleteEntry(entry.id);
    load();
  };

  const handleDeleteFromForm = async (entry) => {
    if (!window.confirm('Delete this entry?')) return;
    await deleteEntry(entry.id);
    setShowForm(false);
    setEditEntry(null);
    load();
  };

  const handleOffDayToggle = async (dateStr, e) => {
    e.stopPropagation();
    if (offDays.has(dateStr)) {
      await removeOffDay(dateStr);
    } else {
      await addOffDay(dateStr);
    }
    load();
  };

  const handleSave = async (data) => {
    if (editEntry) {
      await updateEntry(editEntry.id, data);
    } else {
      await createEntry(data);
    }
    setShowForm(false);
    setEditEntry(null);
    load();
  };

  const nowStr = () => {
    const d = new Date();
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  };

  const handlePunchIn = async () => {
    const today = new Date().toISOString().slice(0, 10);
    await createEntry({ date: today, clock_in: nowStr() });
    load();
  };

  const handlePunchOut = async (entry) => {
    await updateEntry(entry.id, { clock_out: nowStr() });
    load();
  };

  // Group entries by date
  const byDate = {};
  entries.forEach((e) => {
    if (!byDate[e.date]) byDate[e.date] = [];
    byDate[e.date].push(e);
  });

  const todayDateStr = new Date().toISOString().slice(0, 10);
  const { year: curY, month: curM } = currentYearMonth();
  const isCurrentMonth = year === curY && month === curM;
  const todayOpenEntry = isCurrentMonth
    ? (byDate[todayDateStr] || []).find(e => !e.clock_out)
    : null;

  const numDays = daysInMonth(year, month);
  const startDay = firstDayOfMonth(year, month);
  const totalHours = entries.reduce((sum, e) => sum + (e.hours || 0), 0);

  const cells = [];
  // Empty cells for offset
  for (let i = 0; i < startDay; i++) {
    cells.push(<div key={`empty-${i}`} className="cal-cell cal-empty" />);
  }

  for (let d = 1; d <= numDays; d++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const dayEntries = byDate[dateStr] || [];
    const dayHours = dayEntries.reduce((s, e) => s + (e.hours || 0), 0);
    const weekend = isWeekend(year, month, d);
    const today = dateStr === new Date().toISOString().slice(0, 10);
    const isOffDay = offDays.has(dateStr);

    cells.push(
      <div
        key={d}
        className={`cal-cell ${weekend ? 'cal-weekend' : ''} ${today ? 'cal-today' : ''} ${dayEntries.length ? 'cal-has-entry' : ''} ${isOffDay ? 'cal-off-day' : ''}`}
        onClick={() => handleDayClick(dateStr)}
      >
        <div className="cal-day-header">
          <span className={`cal-day-num ${today ? 'today-num' : ''}`}>{d}</span>
          <div className="cal-day-meta">
            {dayHours > 0 && <span className="cal-day-hours">{formatHours(dayHours)}</span>}
            {!weekend && (
              <button
                className={`cal-off-btn${isOffDay ? ' cal-off-btn-on' : ''}`}
                onClick={(e) => handleOffDayToggle(dateStr, e)}
                title={isOffDay ? 'Remove no-work marker' : 'Mark as no work (holiday)'}
              >⊘</button>
            )}
          </div>
        </div>
        <div className="cal-entries">
          {dayEntries.map((entry) => (
            <div key={entry.id} className={`cal-entry${!entry.clock_out ? ' cal-entry-open' : ''}`} onClick={(e) => handleEditClick(entry, e)}>
              <div className="cal-entry-left">
                <span className="cal-entry-time">{entry.clock_in}{entry.clock_out ? `–${entry.clock_out}` : ' →'}</span>
                {entry.note && (
                  <span className="cal-entry-note" data-note={entry.note}>◆</span>
                )}
              </div>
              <button className="cal-entry-del" onClick={(e) => handleDeleteClick(entry, e)} title="Delete">×</button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="month-view">
      <MonthNav year={year} month={month} onChange={handleMonthChange} />

      {isCurrentMonth && (
        <div className={`punch-panel ${todayOpenEntry ? 'punch-open' : 'punch-idle'}`}>
          {todayOpenEntry ? (
            <>
              <div className="punch-status">
                <span className="punch-dot punch-dot-active" />
                <span className="punch-label">PUNCHED IN AT <strong>{todayOpenEntry.clock_in}</strong></span>
              </div>
              <button className="btn-punch btn-punch-out" onClick={() => handlePunchOut(todayOpenEntry)}>PUNCH OUT</button>
            </>
          ) : (
            <>
              <div className="punch-status">
                <span className="punch-dot" />
                <span className="punch-label">NOT PUNCHED IN TODAY</span>
              </div>
              <button className="btn-punch btn-punch-in" onClick={handlePunchIn}>PUNCH IN</button>
            </>
          )}
        </div>
      )}

      <div className="month-summary">
        <span className="month-total-label">TOTAL</span>
        <span className="month-total-value">{formatHours(totalHours)}</span>
        <span className="month-total-sub">logged this month</span>
      </div>

      <div className="cal-weekdays">
        {['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'].map((d) => (
          <div key={d} className="cal-weekday">{d}</div>
        ))}
      </div>

      <div className={`cal-grid ${loading ? 'cal-loading' : ''}`}>
        {cells}
      </div>

      {showForm && (
        <EntryForm
          entry={editEntry}
          date={selectedDate}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditEntry(null); }}
          onDelete={handleDeleteFromForm}
        />
      )}
    </div>
  );
}
