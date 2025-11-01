/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** NotionWebhookSummary - Summary of Notion webhooks on service detail page
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionWebhookSummaryProps {
  user: {
    id?: number | string;
    username?: string;
  } | null;
  isOAuthConnected: boolean;
}

interface WebhookSubscription {
  webhook_id: string;
  status: string;
  event_count: number;
  created_at: string;
}

interface WebhookStats {
  webhooks_configured: boolean;
  subscriptions: WebhookSubscription[];
}

const NotionWebhookSummary: React.FC<NotionWebhookSummaryProps> = ({
  user,
  isOAuthConnected,
}) => {
  const [stats, setStats] = useState<WebhookStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !isOAuthConnected) {
      setLoading(false);
      return;
    }

    fetchWebhookStats();
  }, [user, isOAuthConnected]);

  const fetchWebhookStats = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE}/api/notion-webhooks/status/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching webhook stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!user || loading) return null;

  const activeWebhooks = stats?.subscriptions.filter((s) => s.status === 'active') || [];
  const totalEvents = activeWebhooks.reduce((sum, w) => sum + w.event_count, 0);

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
          <h3 className="text-lg font-semibold text-white mb-2">Real-time Webhooks</h3>

          {activeWebhooks.length > 0 ? (
            <div className="space-y-3">
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-300">
                    {activeWebhooks.length} Webhook{activeWebhooks.length > 1 ? 's' : ''} Active
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-xs text-gray-300">
                  <div>
                    <p className="text-gray-400">Total events received</p>
                    <p className="text-lg font-semibold text-white">{totalEvents}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Mode</p>
                    <p className="text-green-400 font-medium">Real-time (instant)</p>
                  </div>
                </div>
              </div>

              <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-3">
                <p className="text-xs text-gray-300 leading-relaxed">
                  ℹ️ Webhooks are automatically managed for your Notion automations. When you
                  create an automation with a Notion trigger, we enable real-time notifications
                  for instant updates (no 5-minute polling delays).
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
              <p className="text-sm text-gray-300 mb-2">
                No active webhooks yet. Create a Notion automation to enable real-time
                notifications!
              </p>
              <div className="text-xs text-gray-400 space-y-1">
                <p>✓ Instant updates (no delays)</p>
                <p>✓ More efficient API usage</p>
                <p>✓ Automatic setup when you create automations</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotionWebhookSummary;
