import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import MonthView from './pages/MonthView';
import WeekView from './pages/WeekView';
import Stats from './pages/Stats';
import LoginPage from './pages/LoginPage';
import { getAuthStatus, logout } from './api/client';
import './App.css';

export default function App() {
  const [authStatus, setAuthStatus] = useState('loading');

  const checkAuth = useCallback(async () => {
    try {
      const data = await getAuthStatus();
      setAuthStatus(data.authenticated ? 'authenticated' : 'unauthenticated');
    } catch {
      setAuthStatus('unauthenticated');
    }
  }, []);

  useEffect(() => { checkAuth(); }, [checkAuth]);

  async function handleLogout() {
    try { await logout(); } catch { /* ignore */ }
    setAuthStatus('unauthenticated');
  }

  if (authStatus === 'loading') return null;

  if (authStatus === 'unauthenticated') {
    return <LoginPage onLogin={() => setAuthStatus('authenticated')} />;
  }

  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <div className="header-left">
            <h1 className="logo">
              <span className="logo-mark">◼</span> PUNCH
            </h1>
            <span className="logo-sub">WORK HOURS TRACKER</span>
          </div>
          <nav className="header-nav">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              MONTH
            </NavLink>
            <NavLink to="/week" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              WEEK
            </NavLink>
            <NavLink to="/stats" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              STATS
            </NavLink>
            <button className="nav-link nav-logout" onClick={handleLogout}>
              SIGN OUT
            </button>
          </nav>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<MonthView />} />
            <Route path="/week" element={<WeekView />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
