/**
 * Debug API Service
 *
 * Provides functions to manually trigger debug actions and retrieve executions
 */

import { API_BASE } from '../utils/helper';
import type { DebugExecutionsResponse, DebugTriggerResponse } from '../types/api';

/**
 * Manually trigger a debug action for an Area
 */
export const triggerDebugAction = async (areaId: number): Promise<DebugTriggerResponse> => {
  const token = localStorage.getItem('access');

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE}/api/debug/trigger/${areaId}/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get recent executions for a debug Area
 */
export const getDebugExecutions = async (areaId: number): Promise<DebugExecutionsResponse> => {
  const token = localStorage.getItem('access');

  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_BASE}/api/debug/executions/${areaId}/`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};
