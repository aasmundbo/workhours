import { useState } from 'react';
import { login } from '../api/client';
import './LoginPage.css';

export default function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(password);
      onLogin();
    } catch {
      setError('Invalid password');
      setPassword('');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-logo">
            <span className="login-logo-mark">◼</span> PUNCH
          </h1>
          <p className="login-sub">WORK HOURS TRACKER</p>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <label className="login-label" htmlFor="password">PASSWORD</label>
          <input
            id="password"
            className="login-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoFocus
            autoComplete="current-password"
          />
          {error && <p className="login-error">{error}</p>}
          <button className="login-btn" type="submit" disabled={loading || !password}>
            {loading ? 'SIGNING IN…' : 'SIGN IN'}
          </button>
        </form>
      </div>
    </div>
  );
}
