/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** GitHubAppCallback
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API_BASE } from '../utils/helper';

/**
 * GitHub App Installation Callback Handler
 *
 * This component handles the callback after a user installs the GitHub App.
 * It links the installation to the user's account via the backend API.
 *
 * Flow:
 * 1. User clicks "Install GitHub App" from GitHubAppBanner
 * 2. GitHub redirects to this page with installation_id and setup_action
 * 3. This component sends installation_id to backend to link it to the user
 * 4. Backend creates/updates GitHubAppInstallation record
 * 5. Redirects user back to where they came from
 *
 * Expected Query Parameters:
 * - installation_id: The GitHub App installation ID
 * - setup_action: 'install' or 'update'
 */

const GitHubAppCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Linking GitHub App installation...');

  const redirectAfterDelay = useCallback(
    (delay: number) => {
      setTimeout(() => {
        // Try to redirect back to where the user came from
        const redirectPath = sessionStorage.getItem('github_app_redirect') || '/services';
        sessionStorage.removeItem('github_app_redirect');
        navigate(redirectPath);
      }, delay);
    },
    [navigate]
  );

  useEffect(() => {
    const handleCallback = async () => {
      // Extract query parameters from GitHub redirect
      const installationId = searchParams.get('installation_id');
      const setupAction = searchParams.get('setup_action');

      // Validate required parameters
      if (!installationId) {
        setStatus('error');
        setMessage('Invalid callback - missing installation_id');
        redirectAfterDelay(3000);
        return;
      }

      try {
        const token = localStorage.getItem('access');
        if (!token) {
          setStatus('error');
          setMessage('Authentication required. Please log in.');
          setTimeout(() => navigate('/login'), 2000);
          return;
        }

        // Link installation to user account
        const response = await fetch(`${API_BASE}/api/github-app/link-installation/`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            installation_id: installationId,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setStatus('success');
          const action = setupAction === 'update' ? 'updated' : 'installed';

          if (data.pending_webhook) {
            setMessage(`GitHub App ${action}! Syncing repository details...`);
          } else {
            setMessage(
              `Successfully ${action} GitHub App for ${data.account_login} (${data.repository_count} repositories)`
            );
          }

          // Clear the banner dismissal flag so it can check status again
          sessionStorage.removeItem('github_app_banner_dismissed');

          // Redirect after success
          redirectAfterDelay(2000);
        } else {
          const errorData = await response.json().catch(() => ({}));
          setStatus('error');
          setMessage(
            errorData.error ||
              errorData.message ||
              errorData.detail ||
              'Failed to link GitHub App installation'
          );
          redirectAfterDelay(3000);
        }
      } catch (error) {
        console.error('Error linking GitHub App:', error);
        setStatus('error');
        setMessage('An unexpected error occurred. Please try again.');
        redirectAfterDelay(3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate, redirectAfterDelay]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Status Icon */}
          <div className="flex justify-center mb-6">
            {status === 'processing' && (
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600"></div>
            )}
            {status === 'success' && (
              <div className="rounded-full h-16 w-16 bg-green-100 flex items-center justify-center">
                <svg
                  className="h-10 w-10 text-green-600"
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
            )}
            {status === 'error' && (
              <div className="rounded-full h-16 w-16 bg-red-100 flex items-center justify-center">
                <svg
                  className="h-10 w-10 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
            )}
          </div>

          {/* Status Title */}
          <h2 className="text-2xl font-bold text-center mb-3">
            {status === 'processing' && 'Processing Installation'}
            {status === 'success' && 'Installation Complete!'}
            {status === 'error' && 'Installation Failed'}
          </h2>

          {/* Status Message */}
          <p className="text-center text-gray-600 mb-6">{message}</p>

          {/* Progress Indicator */}
          {status === 'processing' && (
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4 overflow-hidden">
              <div
                className="bg-purple-600 h-2 rounded-full animate-pulse"
                style={{ width: '60%' }}
              ></div>
            </div>
          )}

          {/* Action Info */}
          <div className="text-center text-sm text-gray-500">
            {status === 'processing' && 'Please wait...'}
            {status === 'success' && 'Redirecting you back...'}
            {status === 'error' && 'Redirecting to services page...'}
          </div>
        </div>

        {/* GitHub Branding */}
        <div className="mt-6 text-center">
          <div className="flex items-center justify-center space-x-2 text-gray-500">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0110 4.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.137 18.163 20 14.418 20 10c0-5.523-4.477-10-10-10z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm">Powered by GitHub Apps</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GitHubAppCallback;
