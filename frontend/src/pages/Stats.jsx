import { useState, useEffect, useCallback } from 'react';
import MonthNav from '../components/MonthNav';
import { getStats } from '../api/client';
import { currentYearMonth, formatHours } from '../utils/dates';
import './Stats.css';

export default function Stats() {
  const { year: initY, month: initM } = currentYearMonth();
  const [year, setYear] = useState(initY);
  const [month, setMonth] = useState(initM);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setStats(await getStats(year, month));
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [year, month]);

  useEffect(() => { load(); }, [load]);

  if (loading || !stats) {
    return (
      <div className="stats-page">
        <MonthNav year={year} month={month} onChange={(y, m) => { setYear(y); setMonth(m); }} />
        <div className="stats-loading">Loading...</div>
      </div>
    );
  }

  const pct = stats.target_hours > 0 ? Math.min((stats.total_hours / stats.target_hours) * 100, 100) : 0;
  const pctExpected = stats.target_hours > 0 ? Math.min((stats.expected_so_far / stats.target_hours) * 100, 100) : 0;

  return (
    <div className="stats-page">
      <MonthNav year={year} month={month} onChange={(y, m) => { setYear(y); setMonth(m); }} />

      {/* Status banner */}
      <div className={`status-banner ${stats.on_track ? 'status-on-track' : 'status-behind'}`}>
        <div className="status-icon">{stats.on_track ? '●' : '▲'}</div>
        <div className="status-content">
          <div className="status-label">{stats.on_track ? 'ON TRACK' : 'BEHIND SCHEDULE'}</div>
          <div className="status-detail">
            {stats.difference >= 0 ? '+' : ''}{formatHours(Math.abs(stats.difference))}
            {stats.difference >= 0 ? ' ahead' : ' behind'} expected pace
          </div>
        </div>
      </div>

      {/* Key metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">LOGGED</div>
          <div className="metric-value">{formatHours(stats.total_hours)}</div>
          <div className="metric-sub">of {formatHours(stats.target_hours)} target</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">EXPECTED</div>
          <div className="metric-value">{formatHours(stats.expected_so_far)}</div>
          <div className="metric-sub">{stats.elapsed_workdays} of {stats.total_workdays} workdays</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">DAILY AVG</div>
          <div className="metric-value">
            {stats.elapsed_workdays > 0 ? formatHours(stats.total_hours / stats.elapsed_workdays) : '0h'}
          </div>
          <div className="metric-sub">target: 8h/day</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-section">
        <div className="progress-header">
          <span className="progress-title">MONTHLY PROGRESS</span>
          <span className="progress-pct">{pct.toFixed(1)}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
          <div className="progress-expected" style={{ left: `${pctExpected}%` }} title={`Expected: ${pctExpected.toFixed(1)}%`} />
        </div>
        <div className="progress-legend">
          <span><span className="legend-swatch legend-actual" /> Actual</span>
          <span><span className="legend-swatch legend-expected" /> Expected</span>
        </div>
      </div>

      {/* Weekly breakdown */}
      <div className="weekly-section">
        <div className="section-title">WEEKLY BREAKDOWN</div>
        <div className="weekly-list">
          {stats.weekly.map((w, i) => {
            const weekPct = Math.min((w.hours / w.target) * 100, 100);
            return (
              <div key={w.week} className="week-row" style={{ animationDelay: `${i * 0.05}s` }}>
                <div className="week-label">
                  <span className="week-id">{w.week}</span>
                  <span className="week-range">{w.start} → {w.end}</span>
                </div>
                <div className="week-bar-wrap">
                  <div className="week-bar">
                    <div
                      className={`week-bar-fill ${w.hours >= w.target ? 'week-bar-met' : 'week-bar-short'}`}
                      style={{ width: `${weekPct}%` }}
                    />
                  </div>
                  <span className="week-hours">{formatHours(w.hours)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
