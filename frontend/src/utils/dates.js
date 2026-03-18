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

const DAY_NAMES = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

export function shortDayName(year, month, day) {
  const d = new Date(year, month - 1, day).getDay();
  return DAY_NAMES[d === 0 ? 6 : d - 1];
}

export function getWeekNumber(year, month, day) {
  const date = new Date(year, month - 1, day);
  const jan4 = new Date(date.getFullYear(), 0, 4);
  const start = new Date(jan4);
  start.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7));
  const diff = (date - start) / 86400000;
  return Math.floor(diff / 7) + 1;
}

export function getWeekDates(year, month, day) {
  const date = new Date(year, month - 1, day);
  const dow = date.getDay();
  const mondayOffset = dow === 0 ? -6 : 1 - dow;
  const monday = new Date(date);
  monday.setDate(date.getDate() + mondayOffset);

  const dates = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    dates.push({
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      day: d.getDate(),
      dateStr: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`,
    });
  }
  return dates;
}
