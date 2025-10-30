/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** TwitchEventSubSection - Integrated Twitch EventSub webhook UI
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface TwitchEventSubSectionProps {
  user: {
    id?: number | string;
    username?: string;
  } | null;
  isOAuthConnected: boolean;
}

interface TwitchSubscription {
  id: number;
  subscription_id: string | null;
  type: string;
  status: string;
  broadcaster_login: string;
}

interface TwitchEventSubStatus {
  subscriptions: TwitchSubscription[];
  webhook_configured: boolean;
}

const TwitchEventSubSection: React.FC<TwitchEventSubSectionProps> = ({
  user,
  isOAuthConnected,
}) => {
  const [status, setStatus] = useState<TwitchEventSubStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enabling, setEnabling] = useState(false);

  useEffect(() => {
    if (!user || !isOAuthConnected) {
      setLoading(false);
      return;
    }

    checkEventSubStatus();
  }, [user, isOAuthConnected]);

  const checkEventSubStatus = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE}/api/twitch-eventsub/status/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        setError(null);
      } else {
        setError('Failed to check EventSub status');
      }
    } catch (err) {
      console.error('Error checking Twitch EventSub status:', err);
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  const handleEnableEvents = async () => {
    setEnabling(true);
    setError(null);

    try {
      const token = localStorage.getItem('access');
      if (!token) return;

      // Subscribe to all available event types
      // Note: channel.follow will automatically use polling fallback if EventSub not available
      const subscriptionTypes = [
        'stream.online',
        'stream.offline',
        'channel.update',
        'channel.subscribe',
        'channel.follow',
      ];

      let successCount = 0;
      let failCount = 0;

      for (const type of subscriptionTypes) {
        try {
          const response = await fetch(`${API_BASE}/api/twitch-eventsub/subscribe/`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              subscription_type: type,
            }),
          });

          if (response.ok) {
            successCount++;
          } else {
            failCount++;
            const errorData = await response.json();
            console.error(`Failed to enable ${type}:`, errorData);
          }
        } catch (err) {
          failCount++;
          console.error(`Error enabling ${type}:`, err);
        }

        // Small delay between requests
        await new Promise((resolve) => setTimeout(resolve, 300));
      }

      if (successCount > 0) {
        // Refresh status
        await checkEventSubStatus();
      }

      if (failCount > 0) {
        setError(`Some events could not be enabled (${failCount} failed)`);
      }
    } catch (err) {
      console.error('Error enabling Twitch events:', err);
      setError('Failed to enable events');
    } finally {
      setEnabling(false);
    }
  };

  if (!user) return null;

  const activeCount = status?.subscriptions.filter((s) => s.status === 'enabled').length || 0;
  const hasActiveSubscriptions = activeCount > 0;

  return (
    <div className="mt-6 pt-6 border-t border-white/10">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex-shrink-0 w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
          <svg
            className="w-6 h-6 text-purple-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-white">Real-time Webhooks</h3>
            <span className="px-2 py-0.5 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-full">
              Recommended
            </span>
          </div>

          <p className="text-sm text-gray-300 mb-3">
            Enable Twitch EventSub webhooks to receive instant event notifications
          </p>

          {/* Status & Action based on state */}
          {!isOAuthConnected ? (
            <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
              <p className="text-sm text-gray-400">
                ⚠️ Complete OAuth connection first to enable webhooks
              </p>
            </div>
          ) : loading ? (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400"></div>
              Checking EventSub status...
            </div>
          ) : error ? (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-sm text-red-300">{error}</p>
              <button
                onClick={checkEventSubStatus}
                className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
              >
                Retry
              </button>
            </div>
          ) : hasActiveSubscriptions ? (
            // Active subscriptions state
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 bg-green-500/20 text-green-300 px-3 py-1.5 rounded-lg border border-green-500/30">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm font-medium">
                    {activeCount} {activeCount === 1 ? 'Event' : 'Events'} Active
                  </span>
                </div>

                <button
                  onClick={checkEventSubStatus}
                  className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors border border-white/20"
                >
                  Refresh Status
                </button>
              </div>

              <div className="mt-3 pt-3 border-t border-white/5">
                <p className="text-xs text-gray-500 flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Webhooks deliver real-time notifications. Follower events use polling as backup.
                </p>
              </div>
            </div>
          ) : (
            // Not enabled state
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 bg-yellow-500/20 text-yellow-300 px-3 py-1.5 rounded-lg border border-yellow-500/30">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm font-medium">Not Enabled</span>
                </div>
              </div>

              {/* Polling Fallback Warning */}
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm text-yellow-300 font-medium">
                      Currently using polling mode
                    </p>
                    <p className="text-xs text-yellow-400 mt-1">
                      Events are checked every 5 minutes. Enable webhooks for instant real-time
                      notifications.
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleEnableEvents}
                disabled={enabling}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg font-medium transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {enabling ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Enabling Events...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Enable Twitch Events
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TwitchEventSubSection;
