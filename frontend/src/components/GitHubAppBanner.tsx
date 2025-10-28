/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** GitHubAppBanner
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface GitHubAppBannerProps {
  user: {
    id?: number | string;
    username?: string;
  } | null;
}

interface GitHubAppStatus {
  installed: boolean;
  installation_id?: number;
  account_login?: string;
  repository_count?: number;
}

const GitHubAppBanner: React.FC<GitHubAppBannerProps> = ({ user }) => {
  const [status, setStatus] = useState<GitHubAppStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check if user has dismissed the banner in this session
    const isDismissed = sessionStorage.getItem('github_app_banner_dismissed');
    if (isDismissed) {
      setDismissed(true);
      setLoading(false);
      return;
    }

    if (!user) {
      setLoading(false);
      return;
    }

    checkGitHubAppStatus();
  }, [user]);

  const checkGitHubAppStatus = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE}/automations/api/github-app/status/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error checking GitHub App status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInstall = () => {
    // Redirect to GitHub App installation URL
    const githubAppName = import.meta.env.VITE_GITHUB_APP_NAME || 'area-automation';
    const installUrl = `https://github.com/apps/${githubAppName}/installations/new`;

    // Store the current URL to redirect back after installation
    sessionStorage.setItem('github_app_redirect', window.location.pathname);

    window.location.href = installUrl;
  };

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem('github_app_banner_dismissed', 'true');
  };

  // Don't show banner if loading, dismissed, or app is already installed
  if (loading || dismissed || !user || (status && status.installed)) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between flex-wrap">
          <div className="flex items-center flex-1 min-w-0">
            <span className="flex p-2 rounded-lg bg-white bg-opacity-20">
              <svg
                className="h-6 w-6 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fillRule="evenodd"
                  d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0110 4.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.137 18.163 20 14.418 20 10c0-5.523-4.477-10-10-10z"
                  clipRule="evenodd"
                />
              </svg>
            </span>
            <div className="ml-3 flex-1">
              <p className="font-medium text-base">
                Connect GitHub to enable automated workflows
              </p>
              <p className="text-sm text-purple-100 mt-1">
                Install our GitHub App to automatically receive webhook events from your repositories
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3 mt-4 sm:mt-0 sm:ml-3">
            <button
              onClick={handleInstall}
              className="flex-shrink-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-purple-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
            >
              <svg
                className="h-4 w-4 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                  clipRule="evenodd"
                />
              </svg>
              Install GitHub App
            </button>
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 inline-flex items-center justify-center h-10 w-10 rounded-md text-purple-100 hover:text-white hover:bg-white hover:bg-opacity-10 focus:outline-none focus:ring-2 focus:ring-white transition-colors"
              aria-label="Dismiss"
            >
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GitHubAppBanner;
