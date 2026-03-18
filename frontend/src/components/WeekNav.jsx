import { monthName, getWeekNumber } from '../utils/dates';
import './WeekNav.css';

export default function WeekNav({ weekDates, onPrev, onNext, onToday }) {
  const mon = weekDates[0];
  const sun = weekDates[6];
  const weekNum = getWeekNumber(mon.year, mon.month, mon.day);

  const crossMonth = mon.month !== sun.month;
  const label = crossMonth
    ? `${monthName(mon.month).toUpperCase().slice(0, 3)}–${monthName(sun.month).toUpperCase().slice(0, 3)} ${sun.year}`
    : `${monthName(mon.month).toUpperCase()} ${mon.year}`;

  return (
    <div className="week-nav">
      <button className="week-nav-btn" onClick={onPrev}>◂ PREV</button>
      <div className="week-nav-center">
        <span className="week-nav-week">WEEK {weekNum}</span>
        <span className="week-nav-label">{label}</span>
        <button className="week-nav-today" onClick={onToday}>TODAY</button>
      </div>
      <button className="week-nav-btn" onClick={onNext}>NEXT ▸</button>
    </div>
  );
}
