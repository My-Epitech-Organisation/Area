import React, { useState } from 'react';
import parseErrors from '../utils/parseErrors';
import { API_BASE } from '../utils/helper';

const Login: React.FC = () => {
  const [email, setemail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setFieldErrors({});
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        if (data.access) localStorage.setItem('access', data.access);
        if (data.refresh) localStorage.setItem('refresh', data.refresh);

        if (email) localStorage.setItem('email', email);

        try {
          const userRes = await fetch(`${API_BASE}/auth/me/`, {
            headers: {
              Authorization: `Bearer ${data.access}`,
            },
          });

          if (userRes.ok) {
            const userData = await userRes.json();
            const userToStore = {
              name: userData.username || userData.email || email || 'User',
              username: userData.username || email || 'User',
              email: userData.email || email,
              id: userData.id || userData.pk,
            };
            localStorage.setItem('user', JSON.stringify(userToStore));
          } else {
            const basicUser = {
              name: email.split('@')[0] || 'User',
              username: email.split('@')[0] || 'User',
              email: email,
              id: 'temp-user',
            };
            localStorage.setItem('user', JSON.stringify(basicUser));
          }
        } catch (userErr) {
          console.error('Could not fetch user details:', userErr);
          const fallbackUser = {
            name: email.split('@')[0] || 'User',
            username: email.split('@')[0] || 'User',
            email: email,
            id: 'temp-user',
          };
          localStorage.setItem('user', JSON.stringify(fallbackUser));
        }

        window.location.replace('/dashboard');
        return;
      }
      const parsed = parseErrors(data);
      setGeneralError(parsed.message || 'Login failed');
      setFieldErrors(parsed.fields || {});
    } catch {
      setGeneralError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen bg-auth-login flex flex-col items-center">
      <header className="w-full pt-20 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-theme-primary">Log in to AREA</h1>
      </header>
      <main className="w-full flex-1 flex items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10"
        >
          <div className="flex flex-col gap-4">
            {generalError && (
              <div className="text-theme-error text-sm p-3 bg-red-900/20 rounded">{generalError}</div>
            )}

            <label className="text-sm text-theme-secondary">email</label>
            <input
              value={email}
              onChange={(e) => setemail(e.target.value)}
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="email"
            />
            {fieldErrors.email && (
              <div className="text-theme-error text-sm">{fieldErrors.email.join(' ')}</div>
            )}

            <label className="text-sm text-theme-secondary">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="password"
            />
            {fieldErrors.password && (
              <div className="text-theme-error text-sm">{fieldErrors.password.join(' ')}</div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 px-6 py-3 rounded-full btn-primary text-black text-lg"
            >
              {loading ? 'Logging in…' : 'Log in'}
            </button>

            <a href="/signup" className="mt-2 text-sm text-theme-secondary underline block text-center">
              Don&apos;t have an account? Sign up
            </a>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Login;
