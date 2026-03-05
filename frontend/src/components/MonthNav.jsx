import { monthName } from '../utils/dates';
import './MonthNav.css';

export default function MonthNav({ year, month, onChange }) {
  const prev = () => {
    const m = month === 1 ? 12 : month - 1;
    const y = month === 1 ? year - 1 : year;
    onChange(y, m);
  };
  const next = () => {
    const m = month === 12 ? 1 : month + 1;
    const y = month === 12 ? year + 1 : year;
    onChange(y, m);
  };

  return (
    <div className="month-nav">
      <button className="month-nav-btn" onClick={prev}>◂ PREV</button>
      <div className="month-nav-label">
        <span className="month-nav-month">{monthName(month).toUpperCase()}</span>
        <span className="month-nav-year">{year}</span>
      </div>
      <button className="month-nav-btn" onClick={next}>NEXT ▸</button>
    </div>
  );
}
