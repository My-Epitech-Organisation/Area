import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API_BASE } from '../utils/helper';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      setError('Invalid or missing reset token. Please request a new password reset.');
    } else {
      setToken(tokenParam);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError('Invalid or missing reset token.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/auth/password-reset/confirm/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: password,
          confirm_password: confirmPassword,
        }),
      });

      if (response.ok) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(
          errorData.error ||
            errorData.detail ||
            errorData.non_field_errors?.[0] ||
            'Failed to reset password. Please try again or request a new reset link.'
        );
      }
    } catch (err) {
      console.error('Error resetting password:', err);
      setError('Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="w-screen min-h-screen bg-auth-login flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10 shadow-xl animate-appear">
          <div className="text-center">
            <div className="mx-auto w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mb-6">
              <svg
                className="w-10 h-10 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-white mb-3">Password Reset Successful!</h2>
            <p className="text-indigo-200 mb-4 text-lg">
              Your password has been successfully reset.
            </p>
            <p className="text-indigo-300">
              Redirecting to login page in a moment...
            </p>
            <div className="mt-6">
              <a
                href="/login"
                className="inline-block px-6 py-3 rounded-full btn-primary text-black font-medium text-lg transition-all duration-300"
              >
                Go to Login
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-screen min-h-screen bg-auth-login flex flex-col items-center">
      <header className="w-full pt-20 pb-6 flex justify-center">
        <h1 className="text-4xl md:text-5xl font-bold text-theme-primary">Reset Your Password</h1>
      </header>
      <main className="w-full flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white/5 p-8 rounded-xl backdrop-blur-sm border border-white/10 shadow-xl animate-appear">
          <p className="text-center text-indigo-200 mb-6">
            Enter your new password below
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

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-theme-secondary mb-2">
                New Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-md bg-transparent border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="Enter new password"
                minLength={8}
              />
              <p className="text-xs text-indigo-300 mt-2">
                Must be at least 8 characters long
              </p>
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-theme-secondary mb-2"
              >
                Confirm New Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-md bg-transparent border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                placeholder="Confirm new password"
                minLength={8}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !token}
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
                  Resetting Password...
                </span>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a
              href="/login"
              className="text-sm text-indigo-300 hover:text-indigo-200 underline transition-colors duration-200"
            >
              ← Back to Login
            </a>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResetPassword;
