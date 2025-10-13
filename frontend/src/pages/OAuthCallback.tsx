import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8080';

const OAuthCallback: React.FC = () => {
  const { provider } = useParams<{ provider: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Completing authentication...');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
  const service = searchParams.get('service');
  const created = searchParams.get('created');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      // If backend already redirected to frontend with summary params
      if (service) {
        // Show success or error based on query params
        if (error) {
          setStatus('error');
          setMessage(errorDescription || `Authentication failed: ${error}`);
          return;
        }

        // Successful server-side connection
        setStatus('success');
        setMessage(`Successfully ${created === 'true' ? 'connected' : 'reconnected'} to ${service}`);
        setTimeout(() => navigate('/services'), 2000);
        return;
      }

      // Handle OAuth error from provider (client-side flow)
      if (error) {
        setStatus('error');
        setMessage(errorDescription || `Authentication failed: ${error}`);
        return;
      }

      // Client-side flow: frontend must exchange code/state with backend
      if (!code || !state || !provider) {
        setStatus('error');
        setMessage('Missing required authentication parameters');
        return;
      }

      try {
        const token = localStorage.getItem('access');
        if (!token) {
          setStatus('error');
          setMessage('You must be logged in to connect services');
          setTimeout(() => navigate('/login'), 2000);
          return;
        }

        // Call the backend callback endpoint (API mode)
        const response = await fetch(
          `${API_BASE}/auth/oauth/${provider}/callback/?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          setStatus('error');
          setMessage(data.message || data.error || 'Failed to connect service');
          return;
        }

        // Success!
        setStatus('success');
        setMessage(data.message || `Successfully connected to ${provider}!`);

        // Redirect to services page after 2 seconds
        setTimeout(() => {
          navigate('/services');
        }, 2000);

      } catch (err) {
        setStatus('error');
        setMessage(err instanceof Error ? err.message : 'An unexpected error occurred');
      }
    };

    handleCallback();
  }, [provider, searchParams, navigate]);

  return (
    <div className="w-screen min-h-screen bg-gradient-to-br from-black/90 via-gray-900/80 to-indigo-950 flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-lg rounded-xl p-8 text-center">
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-white mb-2">Connecting...</h2>
            <p className="text-gray-300">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Success!</h2>
            <p className="text-green-300 mb-4">{message}</p>
            <p className="text-gray-400 text-sm">Redirecting to services...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Connection Failed</h2>
            <p className="text-red-300 mb-6">{message}</p>
            <button
              onClick={() => navigate('/services')}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition"
            >
              Back to Services
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;
