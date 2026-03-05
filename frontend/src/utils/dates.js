const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export function monthName(month) {
  return MONTHS[month - 1] || '';
}

export function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

export function firstDayOfMonth(year, month) {
  const d = new Date(year, month - 1, 1).getDay();
  // Convert Sunday=0 to Monday=0 based week
  return d === 0 ? 6 : d - 1;
}

export function isWeekend(year, month, day) {
  const d = new Date(year, month - 1, day).getDay();
  return d === 0 || d === 6;
}

export function formatHours(h) {
  const hrs = Math.floor(h);
  const mins = Math.round((h - hrs) * 60);
  return mins > 0 ? `${hrs}h ${mins}m` : `${hrs}h`;
}

export function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export function currentYearMonth() {
  const d = new Date();
  return { year: d.getFullYear(), month: d.getMonth() + 1 };
}
