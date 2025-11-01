/**
 * EPITECH PROJECT, 2025
 * Area
 * File description:
 * NotionWebhookSection - Component for displaying Notion webhook configuration
 */

import React, { useState, useEffect } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionWebhookSectionProps {
  isOAuthConnected: boolean;
}

interface WebhookStatus {
  service: string;
  webhook_configured: boolean;
  webhook_url: string;
  active_subscriptions: number;
  supported_events: string[];
  polling_enabled: boolean;
  recommendation: string;
}

const NotionWebhookSection: React.FC<NotionWebhookSectionProps> = ({ isOAuthConnected }) => {
  const [webhookStatus, setWebhookStatus] = useState<WebhookStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOAuthConnected) {
      fetchWebhookStatus();
    } else {
      setLoading(false);
    }
  }, [isOAuthConnected]);

  const fetchWebhookStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch(`${API_BASE}/api/webhooks/status/notion/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setWebhookStatus(data);
      }
    } catch (error) {
      console.error('Error fetching webhook status:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOAuthConnected) {
    return (
      <div className="mt-6 p-6 bg-gray-800 rounded-lg border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2">⚡ Real-time Webhooks</h3>
        <p className="text-gray-400 text-sm">
          Connect your Notion account via OAuth to enable webhook configuration.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mt-6 p-6 bg-gray-800 rounded-lg border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2">⚡ Real-time Webhooks</h3>
        <p className="text-gray-400 text-sm">Loading webhook status...</p>
      </div>
    );
  }

  if (!webhookStatus) {
    return null;
  }

  const { webhook_configured, webhook_url, polling_enabled, recommendation, supported_events } =
    webhookStatus;

  return (
    <div className="mt-6 p-6 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">⚡ Real-time Webhooks</h3>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            webhook_configured ? 'bg-green-900 text-green-200' : 'bg-yellow-900 text-yellow-200'
          }`}
        >
          {webhook_configured ? '✅ Enabled' : '⚠️ Polling Mode'}
        </span>
      </div>

      <div className="space-y-4">
        {/* Status message */}
        <div
          className={`p-4 rounded-lg ${
            webhook_configured
              ? 'bg-green-900/20 border border-green-700'
              : 'bg-yellow-900/20 border border-yellow-700'
          }`}
        >
          <p className="text-sm text-gray-300">{recommendation}</p>
        </div>

        {/* Webhook URL */}
        {!webhook_configured && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                📍 Webhook URL to configure in Notion:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={webhook_url}
                  readOnly
                  className="flex-1 px-3 py-2 bg-gray-900 border border-gray-600 rounded-lg text-gray-300 text-sm font-mono"
                />
                <button
                  onClick={() => copyToClipboard(webhook_url)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  {copied ? '✓ Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            {/* Configuration instructions */}
            <div className="bg-gray-900 p-4 rounded-lg space-y-3">
              <h4 className="font-semibold text-white text-sm">📖 Setup Instructions:</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-300">
                <li>
                  Go to your{' '}
                  <a
                    href="https://www.notion.so/my-integrations"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:underline"
                  >
                    Notion Integrations page
                  </a>
                </li>
                <li>Select your integration</li>
                <li>Scroll to &quot;Webhooks&quot; section</li>
                <li>Click &quot;Add webhook endpoint&quot; and paste the URL above</li>
                <li>
                  Select API version:{' '}
                  <code className="bg-gray-800 px-2 py-0.5 rounded">2022-06-28</code>
                </li>
                <li>Select events to listen to (see below)</li>
                <li>Save the webhook and copy the secret key</li>
                <li>Contact your admin to add the secret to server configuration</li>
              </ol>
            </div>

            {/* Supported events */}
            <div className="bg-gray-900 p-4 rounded-lg">
              <h4 className="font-semibold text-white text-sm mb-2">
                📡 Recommended Events to Enable:
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {supported_events.map((event) => (
                  <div
                    key={event}
                    className="px-3 py-2 bg-gray-800 rounded text-sm text-gray-300 font-mono"
                  >
                    {event}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Benefits section */}
        <div className="bg-gray-900 p-4 rounded-lg space-y-2">
          <h4 className="font-semibold text-white text-sm">
            {webhook_configured ? '✨ Active Benefits:' : '💡 Webhook Benefits:'}
          </h4>
          <ul className="space-y-1 text-sm text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-0.5">✓</span>
              <span>Instant notifications (no 5-minute polling delay)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-0.5">✓</span>
              <span>Reduced server load and API calls</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-0.5">✓</span>
              <span>More reliable event detection</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-0.5">✓</span>
              <span>Better user experience with real-time automations</span>
            </li>
          </ul>
        </div>

        {/* Current mode */}
        <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-700">
          Current mode: {polling_enabled ? '🔄 Polling every 5 minutes' : '⚡ Real-time webhooks'}
        </div>
      </div>
    </div>
  );
};

export default NotionWebhookSection;
