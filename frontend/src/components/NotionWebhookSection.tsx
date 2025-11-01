/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** NotionWebhookSection - Notion webhook management UI
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionWebhookSectionProps {
  user: {
    id?: number | string;
    username?: string;
  } | null;
  isOAuthConnected: boolean;
  pageId?: string;
  databaseId?: string;
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
  pageId,
  databaseId,
}) => {
  const [status, setStatus] = useState<NotionWebhookStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

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

  const handleCreateWebhook = async () => {
    if (!pageId && !databaseId) {
      setError('Page ID or Database ID is required');
      return;
    }

    setCreating(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setError('Not authenticated');
        setCreating(false);
        return;
      }

      const payload: {
        page_id?: string;
        database_id?: string;
        event_types?: string[];
      } = {};

      if (pageId) {
        payload.page_id = pageId;
        payload.event_types = ['page.updated'];
      }
      if (databaseId) {
        payload.database_id = databaseId;
        payload.event_types = ['database.updated'];
      }

      const response = await fetch(`${API_BASE}/api/notion-webhooks/create/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(data.message || 'Webhook created successfully!');
        await checkWebhookStatus(); // Refresh status
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to create webhook');
      }
    } catch (err) {
      console.error('Error creating Notion webhook:', err);
      setError('Failed to create webhook');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteWebhook = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await fetch(
        `${API_BASE}/api/notion-webhooks/${webhookId}/delete/`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        setSuccess('Webhook deleted successfully');
        await checkWebhookStatus(); // Refresh status
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to delete webhook');
      }
    } catch (err) {
      console.error('Error deleting Notion webhook:', err);
      setError('Failed to delete webhook');
    }
  };

  // Find relevant webhook for current page/database
  const relevantWebhook = status?.subscriptions.find(
    (sub) =>
      (pageId && sub.page_id === pageId) ||
      (databaseId && sub.database_id === databaseId)
  );

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
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-full">
              Recommended
            </span>
          </div>

          <p className="text-sm text-gray-300 mb-3">
            Enable webhooks to receive instant notifications when your Notion content
            changes
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
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
              Checking webhook status...
            </div>
          ) : error && !success ? (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-sm text-red-300">{error}</p>
              <button
                onClick={checkWebhookStatus}
                className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
              >
                Retry
              </button>
            </div>
          ) : relevantWebhook && relevantWebhook.status === 'active' ? (
            // Webhook configured
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-300">
                      Webhook Active
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-1">
                    Created:{' '}
                    {new Date(relevantWebhook.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-gray-400">
                    Events received: {relevantWebhook.event_count}
                  </p>
                  {relevantWebhook.last_event_at && (
                    <p className="text-xs text-gray-400">
                      Last event:{' '}
                      {new Date(relevantWebhook.last_event_at).toLocaleString()}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteWebhook(relevantWebhook.webhook_id)}
                  className="px-3 py-1.5 text-xs font-medium text-red-300 hover:text-red-200 hover:bg-red-500/20 rounded-lg transition-colors"
                  title="Delete webhook"
                >
                  Delete
                </button>
              </div>
              <div className="mt-3 pt-3 border-t border-green-500/20">
                <p className="text-xs text-green-200">
                  ✓ Real-time notifications enabled • No polling delays
                </p>
              </div>
            </div>
          ) : (
            // Not configured - show installation prompt
            <div>
              {success && (
                <div className="mb-3 bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                  <p className="text-sm text-green-300">✓ {success}</p>
                </div>
              )}
              <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3 mb-3">
                  <div className="flex-shrink-0 w-5 h-5 bg-blue-500/20 rounded flex items-center justify-center">
                    <span className="text-xs text-blue-400">i</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-300 mb-2">
                      Without webhooks, we'll check for updates every 5 minutes
                      (polling). Enable webhooks for instant updates!
                    </p>
                    <ul className="text-xs text-gray-400 space-y-1">
                      <li>✓ Instant notifications (no delays)</li>
                      <li>✓ More efficient API usage</li>
                      <li>✓ Better reliability</li>
                    </ul>
                  </div>
                </div>
                <button
                  onClick={handleCreateWebhook}
                  disabled={creating || (!pageId && !databaseId)}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {creating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Creating webhook...
                    </>
                  ) : (
                    <>
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
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                      Enable Real-time Webhooks
                    </>
                  )}
                </button>
                {!pageId && !databaseId && (
                  <p className="mt-2 text-xs text-red-400">
                    Configure a page or database in your Area settings first
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Show all webhooks if multiple exist */}
          {status?.subscriptions && status.subscriptions.length > 1 && (
            <div className="mt-4">
              <details className="text-sm">
                <summary className="cursor-pointer text-gray-400 hover:text-gray-300">
                  View all webhooks ({status.subscriptions.length})
                </summary>
                <div className="mt-2 space-y-2">
                  {status.subscriptions.map((sub) => (
                    <div
                      key={sub.webhook_id}
                      className="bg-white/5 border border-white/10 rounded p-2 text-xs"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-gray-300">
                            {sub.page_id ? 'Page' : 'Database'}: {sub.page_id || sub.database_id}
                          </p>
                          <p className="text-gray-500">Events: {sub.event_count}</p>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotionWebhookSection;
