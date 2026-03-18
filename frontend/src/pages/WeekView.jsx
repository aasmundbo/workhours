import { useState, useEffect, useCallback } from 'react';
import WeekNav from '../components/WeekNav';
import EntryForm from '../components/EntryForm';
import { getEntries, createEntry, updateEntry, deleteEntry, getOffDays, addOffDay, removeOffDay } from '../api/client';
import { getWeekDates, shortDayName, isWeekend, formatHours, todayStr } from '../utils/dates';
import './WeekView.css';

export default function WeekView() {
  const today = new Date();
  const [anchor, setAnchor] = useState({ year: today.getFullYear(), month: today.getMonth() + 1, day: today.getDate() });
  const [entries, setEntries] = useState([]);
  const [offDays, setOffDays] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editEntry, setEditEntry] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

  const weekDates = getWeekDates(anchor.year, anchor.month, anchor.day);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const months = new Set(weekDates.map(d => `${d.year}-${d.month}`));
      const fetches = [...months].map(key => {
        const [y, m] = key.split('-').map(Number);
        return Promise.all([getEntries(y, m), getOffDays(y, m)]);
      });
      const results = await Promise.all(fetches);
      const allEntries = results.flatMap(([e]) => e);
      const allOffDays = results.flatMap(([, o]) => o);
      setEntries(allEntries);
      setOffDays(new Set(allOffDays));
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [anchor.year, anchor.month, anchor.day]);

  useEffect(() => { load(); }, [load]);

  const shiftWeek = (dir) => {
    const d = new Date(anchor.year, anchor.month - 1, anchor.day + dir * 7);
    setAnchor({ year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate() });
  };

  const goToday = () => {
    const d = new Date();
    setAnchor({ year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate() });
  };

  const handleDayClick = (dateStr) => {
    setSelectedDate(dateStr);
    setEditEntry(null);
    setShowForm(true);
  };

  const handleEditClick = (entry) => {
    setEditEntry(entry);
    setSelectedDate(null);
    setShowForm(true);
  };

  const handleDeleteClick = async (entry) => {
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

  const handleOffDayToggle = async (dateStr) => {
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
    await createEntry({ date: todayStr(), clock_in: nowStr() });
    load();
  };

  const handlePunchOut = async (entry) => {
    await updateEntry(entry.id, { clock_out: nowStr() });
    load();
  };

  const byDate = {};
  entries.forEach((e) => {
    if (!byDate[e.date]) byDate[e.date] = [];
    byDate[e.date].push(e);
  });

  const weekDateStrs = new Set(weekDates.map(d => d.dateStr));
  const todayDateStr = todayStr();
  const isCurrentWeek = weekDateStrs.has(todayDateStr);
  const todayOpenEntry = isCurrentWeek
    ? (byDate[todayDateStr] || []).find(e => !e.clock_out)
    : null;

  const weekHours = weekDates.reduce((sum, d) => {
    const dayEntries = byDate[d.dateStr] || [];
    return sum + dayEntries.reduce((s, e) => s + (e.hours || 0), 0);
  }, 0);

  return (
    <div className="week-view">
      <WeekNav
        weekDates={weekDates}
        onPrev={() => shiftWeek(-1)}
        onNext={() => shiftWeek(1)}
        onToday={goToday}
      />

      {isCurrentWeek && (
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
                <span className="punch-label">NOT PUNCHED IN</span>
              </div>
              <button className="btn-punch btn-punch-in" onClick={handlePunchIn}>PUNCH IN</button>
            </>
          )}
        </div>
      )}

      <div className="week-summary">
        <span className="week-total-label">TOTAL</span>
        <span className="week-total-value">{formatHours(weekHours)}</span>
        <span className="week-total-sub">this week</span>
      </div>

      <div className={`week-days ${loading ? 'week-loading' : ''}`}>
        {weekDates.map(({ year, month, day, dateStr }) => {
          const dayEntries = byDate[dateStr] || [];
          const dayHours = dayEntries.reduce((s, e) => s + (e.hours || 0), 0);
          const weekend = isWeekend(year, month, day);
          const isToday = dateStr === todayDateStr;
          const isOff = offDays.has(dateStr);
          const dayName = shortDayName(year, month, day);

          return (
            <div
              key={dateStr}
              className={`week-day${weekend ? ' week-day-weekend' : ''}${isToday ? ' week-day-today' : ''}${isOff ? ' week-day-off' : ''}`}
            >
              <div className="week-day-header" onClick={() => handleDayClick(dateStr)}>
                <div className="week-day-label">
                  <span className="week-day-name">{dayName}</span>
                  <span className={`week-day-num${isToday ? ' week-day-num-today' : ''}`}>{day}</span>
                </div>
                <div className="week-day-meta">
                  {dayHours > 0 && <span className="week-day-hours">{formatHours(dayHours)}</span>}
                  {!weekend && (
                    <button
                      className={`week-off-btn${isOff ? ' week-off-btn-on' : ''}`}
                      onClick={(e) => { e.stopPropagation(); handleOffDayToggle(dateStr); }}
                      title={isOff ? 'Remove no-work marker' : 'Mark as no work'}
                    >⊘</button>
                  )}
                </div>
              </div>

              <div className="week-day-entries">
                {dayEntries.length === 0 && (
                  <div className="week-day-empty" onClick={() => handleDayClick(dateStr)}>
                    tap to add entry
                  </div>
                )}
                {dayEntries.map((entry) => (
                  <div
                    key={entry.id}
                    className={`week-entry${!entry.clock_out ? ' week-entry-open' : ''}`}
                    onClick={() => handleEditClick(entry)}
                  >
                    <div className="week-entry-main">
                      <span className="week-entry-time">
                        {entry.clock_in}{entry.clock_out ? `–${entry.clock_out}` : ' →'}
                      </span>
                      {entry.hours != null && (
                        <span className="week-entry-hrs">{formatHours(entry.hours)}</span>
                      )}
                      <button
                        className="week-entry-del"
                        onClick={(e) => { e.stopPropagation(); handleDeleteClick(entry); }}
                        title="Delete"
                      >×</button>
                    </div>
                    {entry.note && (
                      <div className="week-entry-note">{entry.note}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
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
