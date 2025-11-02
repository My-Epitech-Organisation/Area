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
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="flex-shrink-0 w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
            <svg
              className="w-6 h-6 text-green-400"
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
              <span className="px-2 py-0.5 text-xs font-medium bg-gray-500/20 text-gray-300 rounded-full">
                Inactive
              </span>
            </div>
            <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
              <p className="text-sm text-gray-400">
                ⚠️ Connect your Notion account via OAuth to enable webhook configuration
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center animate-pulse">
            <svg
              className="w-6 h-6 text-green-400"
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
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white mb-2">Real-time Webhooks</h3>
            <p className="text-sm text-gray-400">Loading webhook status...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!webhookStatus) {
    return null;
  }

  const { webhook_configured, webhook_url, polling_enabled, recommendation, supported_events } =
    webhookStatus;

  return (
    <div className="mt-6 pt-6 border-t border-white/10">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex-shrink-0 w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
          <svg
            className="w-6 h-6 text-green-400"
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
            <span
              className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                webhook_configured
                  ? 'bg-green-500/20 text-green-300'
                  : 'bg-yellow-500/20 text-yellow-300'
              }`}
            >
              {webhook_configured ? 'Active' : 'Polling Mode'}
            </span>
          </div>

          <div className="space-y-3">
            {/* Status message */}
            <div
              className={`rounded-lg p-3 border ${
                webhook_configured
                  ? 'bg-green-500/10 border-green-500/30'
                  : 'bg-yellow-500/10 border-yellow-500/30'
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
                <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3 space-y-3">
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
                <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
                  <h4 className="font-semibold text-white text-sm mb-2">
                    📡 Recommended Events to Enable:
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {supported_events.map((event) => (
                      <div
                        key={event}
                        className="px-2 py-1.5 bg-gray-800/50 rounded text-xs text-gray-300 font-mono"
                      >
                        {event}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Benefits section - only show when webhook is configured */}
            {webhook_configured && (
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5"
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
                    <p className="text-sm text-green-300 font-medium">Instant notifications</p>
                    <p className="text-xs text-green-400 mt-1">
                      Your automations react immediately when events occur - no delays from polling
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Current mode footer */}
            <div className="text-xs text-gray-500 text-center pt-2">
              Current mode:{' '}
              {polling_enabled ? '🔄 Polling every 5 minutes' : '⚡ Real-time webhooks'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotionWebhookSection;
