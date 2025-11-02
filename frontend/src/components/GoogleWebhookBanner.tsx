/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** GoogleWebhookBanner - Informative banner for Google webhook services
 */

import React from 'react';

interface GoogleWebhookBannerProps {
  serviceName: string;
  isOAuthConnected: boolean;
}

const GoogleWebhookBanner: React.FC<GoogleWebhookBannerProps> = ({
  serviceName,
  isOAuthConnected,
}) => {
  // Get display name
  const displayName =
    serviceName.toLowerCase() === 'youtube'
      ? 'YouTube'
      : serviceName.toLowerCase() === 'google_calendar'
        ? 'Google Calendar'
        : serviceName;

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
            <span className="px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-300 rounded-full">
              Active
            </span>
          </div>

          {isOAuthConnected ? (
            // Connected state - webhooks active
            <div className="space-y-3">
              <p className="text-sm text-gray-300">
                ⚡ {displayName} events are delivered instantly through real-time webhooks
              </p>

              <div className="flex items-center gap-2 bg-green-500/20 text-green-300 px-3 py-2 rounded-lg border border-green-500/30">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium">Webhooks Enabled</span>
              </div>

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
            </div>
          ) : (
            // Not connected state
            <div className="bg-gray-500/10 border border-gray-500/30 rounded-lg p-3">
              <p className="text-sm text-gray-400">
                ⚠️ Connect your Google account to enable real-time webhook notifications
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoogleWebhookBanner;
