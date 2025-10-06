import React, { useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

const Signup: React.FC = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  const parseErrors = (errBody: any): { message: string; fields?: Record<string, string[]> } => {
    if (!errBody)
      return { message: 'An error occurred' };
    if (typeof errBody === 'string')
      return { message: errBody };
    if (errBody.detail)
      return { message: String(errBody.detail) };
    if (typeof errBody === 'object') {
      const fields: Record<string, string[]> = {};
      const parts: string[] = [];
      for (const k of Object.keys(errBody)) {
        const v = errBody[k];
        if (Array.isArray(v)) {
          fields[k] = v.map((s) => String(s));
          parts.push(`${k}: ${v.join(' ')}`);
        } else if (typeof v === 'string') {
          fields[k] = [v];
          parts.push(`${k}: ${v}`);
        }
      }
      return { message: parts.join(' — '), fields };
    }
    return { message: 'An error occurred' };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setFieldErrors({});
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, password2 }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        if (data.access)
          localStorage.setItem('access', data.access);
        if (data.refresh)
          localStorage.setItem('refresh', data.refresh);
        window.location.href = '/dashboard';
        return;
      }
      const parsed = parseErrors(data);
      setGeneralError(parsed.message || 'Registration failed');
      setFieldErrors(parsed.fields || {});
    } catch (err) {
      setGeneralError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen bg-auth-signup flex flex-col items-center">
      <header className="w-full pt-20 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-white">Create an account</h1>
      </header>
      <main className="w-full flex-1 flex items-center justify-center">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10"
        >
          <div className="flex flex-col gap-4">
            {generalError && <div className="text-red-400 text-sm p-3 bg-red-900/20 rounded">{generalError}</div>}

            <label className="text-sm text-gray-300">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="username"
            />
            {fieldErrors.username && <div className="text-red-400 text-sm">{fieldErrors.username.join(' ')}</div>}

            <label className="text-sm text-gray-300">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="you@example.com"
            />
            {fieldErrors.email && <div className="text-red-400 text-sm">{fieldErrors.email.join(' ')}</div>}

            <label className="text-sm text-gray-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="password"
            />
            {fieldErrors.password && <div className="text-red-400 text-sm">{fieldErrors.password.join(' ')}</div>}

            <label className="text-sm text-gray-300">Verify password</label>
            <input
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="repeat password"
            />
            {fieldErrors.password2 && <div className="text-red-400 text-sm">{fieldErrors.password2.join(' ')}</div>}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 px-6 py-3 rounded-full btn-primary text-black text-lg"
            >
              {loading ? 'Registering…' : 'Register'}
            </button>

            <button
              type="button"
              onClick={() => (window.location.href = '/login')}
              className="mt-2 text-sm text-gray-300 underline"
            >
              Already have an account? Log in
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Signup;