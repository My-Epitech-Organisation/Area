/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** NotionWebhookSection - Auto-managed webhook status display
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionWebhookSectionProps {
  user: {
    id?: number | string;
    username?: string;
  } | null;
  isOAuthConnected: boolean;
}

interface WebhookSubscription {
  webhook_id: string;
  workspace_id: string;
  page_id: string;
  database_id: string;
  event_types: string[];
  status: string;
  created_at: string;
  event_count: number;
  last_event_at: string | null;
}

interface NotionWebhookStatus {
  webhooks_configured: boolean;
  subscriptions: WebhookSubscription[];
}

const NotionWebhookSection: React.FC<NotionWebhookSectionProps> = ({
  user,
  isOAuthConnected,
}) => {
  const [status, setStatus] = useState<NotionWebhookStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !isOAuthConnected) {
      setLoading(false);
      return;
    }

    checkWebhookStatus();
  }, [user, isOAuthConnected]);

  const checkWebhookStatus = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE}/api/notion-webhooks/status/`, {
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
        setError('Failed to check webhook status');
      }
    } catch (err) {
      console.error('Error checking Notion webhook status:', err);
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="mt-6 pt-6 border-t border-white/10">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex-shrink-0 w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
          <svg
            className="w-6 h-6 text-blue-400"
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
            <span className="px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-300 rounded-full">
              Auto-managed
            </span>
          </div>

          <p className="text-sm text-gray-300 mb-3">
            Webhooks are automatically configured when you create Notion automations
          </p>

          {/* Status Display */}
          {!isOAuthConnected ? (
            <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-4">
              <p className="text-sm text-gray-400">
                ⚠️ Complete OAuth connection to enable automatic webhook management
              </p>
            </div>
          ) : loading ? (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
              Checking webhook status...
            </div>
          ) : error ? (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-sm text-red-300">{error}</p>
              <button
                onClick={checkWebhookStatus}
                className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
              >
                Retry
              </button>
            </div>
          ) : status?.webhooks_configured && status.subscriptions.length > 0 ? (
            // Webhooks exist - show auto-managed status
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-300">
                  ✓ Webhooks Automatically Configured
                </span>
              </div>
              <div className="space-y-2 mb-3">
                <p className="text-xs text-gray-300">
                  <strong>{status.subscriptions.length}</strong> webhook
                  {status.subscriptions.length > 1 ? 's' : ''} active
                </p>
                <p className="text-xs text-gray-400">
                  Total events received:{' '}
                  {status.subscriptions.reduce((sum, sub) => sum + sub.event_count, 0)}
                </p>
              </div>
              <div className="pt-3 border-t border-green-500/20">
                <p className="text-xs text-green-200">
                  ✓ Real-time notifications enabled • Managed automatically
                </p>
              </div>

              {/* Show webhook details if multiple exist */}
              {status.subscriptions.length > 1 && (
                <details className="mt-3 text-sm">
                  <summary className="cursor-pointer text-gray-400 hover:text-gray-300 text-xs">
                    View all webhooks ({status.subscriptions.length})
                  </summary>
                  <div className="mt-2 space-y-2">
                    {status.subscriptions.map((sub) => (
                      <div
                        key={sub.webhook_id}
                        className="bg-white/5 border border-white/10 rounded p-2 text-xs"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="text-gray-300 mb-1">
                              {sub.page_id ? '📄 Page' : '🗂️ Database'}:{' '}
                              {(sub.page_id || sub.database_id).substring(0, 8)}...
                            </p>
                            <p className="text-gray-500">
                              Events: {sub.event_count} • Created:{' '}
                              {new Date(sub.created_at).toLocaleDateString()}
                            </p>
                            {sub.last_event_at && (
                              <p className="text-gray-500">
                                Last event: {new Date(sub.last_event_at).toLocaleString()}
                              </p>
                            )}
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-xs flex-shrink-0 ${
                              sub.status === 'active'
                                ? 'bg-green-500/20 text-green-300'
                                : 'bg-gray-500/20 text-gray-400'
                            }`}
                          >
                            {sub.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ) : (
            // No webhooks yet - show guidance
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
              <div className="flex items-start gap-3 mb-3">
                <div className="flex-shrink-0 w-5 h-5 bg-blue-500/20 rounded flex items-center justify-center">
                  <span className="text-xs text-blue-400">i</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-300 mb-3 font-medium">
                    ℹ️ How it works
                  </p>
                  <ul className="text-xs text-gray-400 space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400 flex-shrink-0">1.</span>
                      <span>
                        When you create a Notion automation, webhooks are{' '}
                        <strong className="text-gray-300">automatically configured</strong>
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400 flex-shrink-0">2.</span>
                      <span>
                        You'll receive <strong className="text-gray-300">instant updates</strong>{' '}
                        when your Notion content changes
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400 flex-shrink-0">3.</span>
                      <span>
                        When you delete an automation, webhooks are{' '}
                        <strong className="text-gray-300">automatically cleaned up</strong>
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-blue-500/20">
                <a
                  href="/Areaction?service=notion"
                  className="inline-flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 hover:underline"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Create your first Notion automation
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotionWebhookSection;
