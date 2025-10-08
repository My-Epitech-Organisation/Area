import React, { useState } from "react";
import parseErrors from "../utils/parseErrors";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

const Login: React.FC = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
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
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: usernameOrEmail, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        if (data.access) localStorage.setItem('access', data.access);
        if (data.refresh) localStorage.setItem('refresh', data.refresh);
        window.location.href = '/dashboard';
        return;
      }
      const parsed = parseErrors(data);
      setGeneralError(parsed.message || 'Login failed');
      setFieldErrors(parsed.fields || {});
    } catch (err) {
      setGeneralError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen bg-auth-login flex flex-col items-center">
      <header className="w-full pt-20 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-white">Log in to AREA</h1>
      </header>
      <main className="w-full flex-1 flex items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10"
        >
          <div className="flex flex-col gap-4">
            {generalError && (
              <div className="text-red-400 text-sm p-3 bg-red-900/20 rounded">{generalError}</div>
            )}

            <label className="text-sm text-gray-300">Username or email</label>
            <input
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="username or email"
            />
            {fieldErrors.username && (
              <div className="text-red-400 text-sm">{fieldErrors.username.join(' ')}</div>
            )}
            {fieldErrors.email && (
              <div className="text-red-400 text-sm">{fieldErrors.email.join(' ')}</div>
            )}

            <label className="text-sm text-gray-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="password"
            />
            {fieldErrors.password && (
              <div className="text-red-400 text-sm">{fieldErrors.password.join(' ')}</div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 px-6 py-3 rounded-full btn-primary text-black text-lg"
            >
              {loading ? 'Logging in…' : 'Log in'}
            </button>

            <a
              href="/signup"
              className="mt-2 text-sm text-gray-300 underline block text-center"
            >
              Don't have an account? Sign up
            </a>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Login;