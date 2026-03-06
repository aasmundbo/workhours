const BASE = '/api';

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export function getEntries(year, month) {
  return request(`/entries?year=${year}&month=${month}`);
}

export function createEntry(data) {
  return request('/entries', { method: 'POST', body: JSON.stringify(data) });
}

export function updateEntry(id, data) {
  return request(`/entries/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export function deleteEntry(id) {
  return request(`/entries/${id}`, { method: 'DELETE' });
}

export function getStats(year, month) {
  return request(`/stats?year=${year}&month=${month}`);
}

export function getOffDays(year, month) {
  return request(`/off-days?year=${year}&month=${month}`);
}

export function addOffDay(date) {
  return request('/off-days', { method: 'POST', body: JSON.stringify({ date }) });
}

export function removeOffDay(date) {
  return request(`/off-days/${date}`, { method: 'DELETE' });
}
