import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import MonthView from './pages/MonthView';
import Stats from './pages/Stats';
import './App.css';

export default function App() {
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
              TIMESHEET
            </NavLink>
            <NavLink to="/stats" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              STATS
            </NavLink>
          </nav>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<MonthView />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
