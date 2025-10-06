import React, { useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8080";

const Signup: React.FC = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, any> | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password, password2 }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        window.location.href = "/dashboard";
      } else {
        setErrors(data || { detail: 'Registration failed' });
      }
    } catch (err) {
      setErrors({ detail: 'Network error' });
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
            <label className="text-sm text-gray-300">Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="your username"
            />

            <label className="text-sm text-gray-300">Email</label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="you@example.com"
            />

            <label className="text-sm text-gray-300">Password</label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="password"
            />

            <label className="text-sm text-gray-300">Verify password</label>
            <input
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              type="password"
              required
              className="px-4 py-3 rounded-md bg-transparent border border-white/20 text-white"
              placeholder="repeat password"
            />

            {errors && (
              <div className="text-red-400 text-sm">
                {typeof errors === 'string' ? errors : JSON.stringify(errors)}
              </div>
            )}

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