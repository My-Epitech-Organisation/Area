/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** NotionWebhookStatus - Compact webhook status badge for Areas
 */

import React, { useEffect, useState } from 'react';
import { API_BASE } from '../utils/helper';

interface NotionWebhookStatusProps {
  areaId: number;
}

interface WebhookStatus {
  has_webhook: boolean;
  status: 'active' | 'inactive' | 'polling';
  event_count: number;
}

const NotionWebhookStatus: React.FC<NotionWebhookStatusProps> = ({ areaId }) => {
  const [status, setStatus] = useState<WebhookStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWebhookStatus();
  }, [areaId]);

  const fetchWebhookStatus = async () => {
    try {
      const token = localStorage.getItem('access');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(
        `${API_BASE}/api/areas/${areaId}/notion-webhook-status/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (err) {
      console.error('Error fetching webhook status:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !status) {
    return null;
  }

  return (
    <div className="inline-flex items-center gap-1.5 ml-2">
      {status.has_webhook && status.status === 'active' ? (
        <>
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs text-green-400 font-medium">Webhook</span>
          {status.event_count > 0 && (
            <span className="text-xs text-gray-500">({status.event_count})</span>
          )}
        </>
      ) : (
        <>
          <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full" />
          <span className="text-xs text-yellow-400">Polling (5min)</span>
        </>
      )}
    </div>
  );
};

export default NotionWebhookStatus;
