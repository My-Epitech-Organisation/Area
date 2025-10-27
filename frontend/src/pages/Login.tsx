import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import parseErrors from '../utils/parseErrors';
import { API_BASE } from '../utils/helper';

const Login: React.FC = () => {
  const [email, setemail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [searchParams, setSearchParams] = useSearchParams();

  // Notification states for email verification
  const [verificationMessage, setVerificationMessage] = useState<string | null>(null);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [showVerificationAlert, setShowVerificationAlert] = useState(false);

  // Check for email verification parameters on component mount
  useEffect(() => {
    const verified = searchParams.get('verified');
    const message = searchParams.get('message');
    const error = searchParams.get('error');
    const emailParam = searchParams.get('email');
    const expired = searchParams.get('expired');

    if (verified === 'true' && message) {
      setVerificationMessage(message);
      setShowVerificationAlert(true);
      if (emailParam) {
        setemail(emailParam); // Pre-fill email field
      }
      // Clear URL parameters after reading them
      setTimeout(() => {
        setSearchParams({});
      }, 100);
    } else if (error) {
      setVerificationError(error);
      setShowVerificationAlert(true);
      // Clear URL parameters after reading them
      setTimeout(() => {
        setSearchParams({});
      }, 100);
    }

    // Auto-hide alerts after 10 seconds
    if (message || error) {
      const timer = setTimeout(() => {
        setShowVerificationAlert(false);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [searchParams, setSearchParams]);

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
            {/* Email Verification Success Alert */}
            {showVerificationAlert && verificationMessage && (
              <div className="text-green-400 text-sm p-4 bg-green-900/20 rounded-lg border border-green-500/30 flex items-start gap-3">
                <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="font-semibold">✓ Email Verified!</p>
                  <p className="text-green-300/90 mt-1">{verificationMessage}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowVerificationAlert(false)}
                  className="text-green-400 hover:text-green-300"
                >
                  ×
                </button>
              </div>
            )}

            {/* Email Verification Error Alert */}
            {showVerificationAlert && verificationError && (
              <div className="text-red-400 text-sm p-4 bg-red-900/20 rounded-lg border border-red-500/30 flex items-start gap-3">
                <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <p className="font-semibold">⚠ Verification Failed</p>
                  <p className="text-red-300/90 mt-1">{verificationError}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowVerificationAlert(false)}
                  className="text-red-400 hover:text-red-300"
                >
                  ×
                </button>
              </div>
            )}

            {generalError && (
              <div className="text-theme-error text-sm p-3 bg-red-900/20 rounded">
                {generalError}
              </div>
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

            <div className="text-right mt-1">
              <a
                href="/forgot-password"
                className="text-sm text-indigo-300 hover:text-indigo-200 underline"
              >
                Forgot password?
              </a>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="mt-2 px-6 py-3 rounded-full btn-primary text-black text-lg"
            >
              {loading ? 'Logging in…' : 'Log in'}
            </button>

            <a
              href="/signup"
              className="mt-2 text-sm text-theme-secondary underline block text-center"
            >
              Don&apos;t have an account? Sign up
            </a>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Login;
