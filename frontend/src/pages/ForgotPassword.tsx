import React, { useState } from 'react';
import { API_BASE } from '../utils/helper';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!email) {
      setError('Please provide an email address');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/password-reset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        setSuccess(
          'If that email exists in our system, a password reset link has been sent. Check your inbox.'
        );
      } else {
        setError(data.error || data.detail || 'Failed to request password reset.');
      }
    } catch (err) {
      console.error('Error requesting password reset:', err);
      setError('Network error. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-screen min-h-screen bg-auth-login flex flex-col items-center">
      <header className="w-full pt-20 pb-6 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-theme-primary">Forgot Password</h1>
      </header>
      <main className="w-full flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10 shadow-xl animate-appear">
          <p className="text-center text-indigo-200 mb-6">
            Enter your email address and we&apos;ll send you a link to reset your password
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-900/20 rounded-lg border border-red-500/30 flex items-start gap-3 animate-slide-up">
              <svg
                className="w-5 h-5 mt-0.5 flex-shrink-0 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-red-200 text-sm">{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-900/20 rounded-lg border border-green-500/30 flex items-start gap-3 animate-slide-up">
              <svg
                className="w-5 h-5 mt-0.5 flex-shrink-0 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-green-200 text-sm">{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-theme-secondary mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-md bg-transparent border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="your.email@example.com"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 px-6 py-3 rounded-full btn-primary text-black font-medium text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Sending…
                </span>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </form>

          <div className="mt-6 text-center space-y-2">
            <a
              href="/login"
              className="block text-sm text-indigo-300 hover:text-indigo-200 underline transition-colors duration-200"
            >
              ← Back to Login
            </a>
            <a
              href="/signup"
              className="block text-sm text-theme-secondary hover:text-indigo-200 underline transition-colors duration-200"
            >
              Don&apos;t have an account? Sign up
            </a>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ForgotPassword;
