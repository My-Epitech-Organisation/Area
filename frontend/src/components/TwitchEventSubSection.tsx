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
  subscription_id: string;
  subscription_type: string;
  status: string;
  broadcaster_login: string;
  broadcaster_user_id: string;
  created_at: string;
}

interface TwitchEventSubStatus {
  has_subscriptions: boolean;
  subscriptions: TwitchSubscription[];
}

const SUBSCRIPTION_TYPES = [
  { value: 'stream.online', label: 'Stream Online', description: 'When stream goes live' },
  { value: 'stream.offline', label: 'Stream Offline', description: 'When stream ends' },
  { value: 'channel.follow', label: 'New Follower', description: 'When someone follows' },
  { value: 'channel.subscribe', label: 'New Subscriber', description: 'When someone subscribes' },
  { value: 'channel.update', label: 'Channel Update', description: 'When channel info changes' },
];

const TwitchEventSubSection: React.FC<TwitchEventSubSectionProps> = ({ user, isOAuthConnected }) => {
  const [status, setStatus] = useState<TwitchEventSubStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subscribing, setSubscribing] = useState(false);

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

  const handleSubscribeType = async (subscriptionType: string) => {
    setError(null);

    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setError('Not authenticated');
        return false;
      }

      const response = await fetch(`${API_BASE}/api/twitch-eventsub/subscribe/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription_type: subscriptionType,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        return true;
      } else {
        setError(data.error || 'Failed to create subscription');
        return false;
      }
    } catch (err) {
      console.error('Error creating subscription:', err);
      setError('Connection error');
      return false;
    }
  };

  const handleEnableAll = async () => {
    setSubscribing(true);
    setError(null);

    let successCount = 0;
    let failCount = 0;

    for (const type of SUBSCRIPTION_TYPES) {
      const success = await handleSubscribeType(type.value);
      if (success) {
        successCount++;
      } else {
        failCount++;
      }
      // Small delay between requests to avoid rate limiting
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    setSubscribing(false);

    // Refresh status to show new subscriptions
    await checkEventSubStatus();

    if (failCount === 0) {
      setError(null);
    } else if (successCount > 0) {
      setError(
        `Enabled ${successCount} events successfully. ${failCount} failed (may already exist).`
      );
    }
  };

  const handleUnsubscribe = async (subscriptionId: number) => {
    if (!window.confirm('Are you sure you want to delete this webhook subscription?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access');
      if (!token) return;

      const response = await fetch(
        `${API_BASE}/api/twitch-eventsub/unsubscribe/${subscriptionId}/`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        // Refresh status
        await checkEventSubStatus();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to delete subscription');
      }
    } catch (err) {
      console.error('Error deleting subscription:', err);
      setError('Connection error');
    }
  };

  const formatSubscriptionType = (type: string): string => {
    const found = SUBSCRIPTION_TYPES.find((t) => t.value === type);
    return found ? found.label : type;
  };

  if (!user) return null;

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
            <h3 className="text-lg font-semibold text-white">Real-time EventSub Webhooks</h3>
            <span className="px-2 py-0.5 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-full">
              Recommended
            </span>
          </div>

          <p className="text-sm text-gray-300 mb-3">
            Enable EventSub to receive instant Twitch event notifications without polling delays
          </p>

          {/* Status & Action based on state */}
          {!isOAuthConnected ? (
            <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
              <p className="text-sm text-gray-400">
                ⚠️ Complete OAuth connection first to enable EventSub webhooks
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
          ) : (
            <div className="space-y-4">
              {/* Active Subscriptions */}
              {status?.has_subscriptions && status.subscriptions.length > 0 && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="text-sm font-semibold text-green-300">
                      Active Subscriptions ({status.subscriptions.length})
                    </span>
                  </div>

                  <div className="space-y-2">
                    {status.subscriptions.map((sub) => (
                      <div
                        key={sub.id}
                        className="flex items-center justify-between bg-black/20 rounded p-3"
                      >
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">
                            {formatSubscriptionType(sub.subscription_type)}
                          </p>
                          {sub.broadcaster_login && (
                            <p className="text-xs text-gray-400 mt-0.5">
                              Channel: {sub.broadcaster_login}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 mt-0.5">
                            Status: {sub.status}
                          </p>
                        </div>
                        <button
                          onClick={() => handleUnsubscribe(sub.id)}
                          className="px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded text-xs font-medium transition-colors border border-red-500/30"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Enable All Events */}
              {!status?.has_subscriptions && (
                <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-lg p-4">
                  <div className="flex items-start gap-3 mb-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-white mb-1">
                        Enable Real-time Notifications
                      </h4>
                      <p className="text-xs text-gray-400">
                        This will enable webhooks for all Twitch events: Stream Online/Offline, New Followers, Subscribers, and Channel Updates
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={handleEnableAll}
                    disabled={subscribing}
                    className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg text-sm font-semibold transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    {subscribing ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Enabling Events...
                      </>
                    ) : (
                      <>
                        <svg
                          className="w-5 h-5"
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
                        Enable All Twitch Events
                      </>
                    )}
                  </button>

                  <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                      />
                    </svg>
                    You can manage individual events after enabling
                  </div>
                </div>
              )}

              {/* Info */}
              <div className="mt-3 pt-3 border-t border-white/5">
                <p className="text-xs text-gray-500 flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  EventSub webhooks provide real-time event notifications (&lt;1s latency)
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TwitchEventSubSection;
