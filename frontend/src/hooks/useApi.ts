/**
 * Custom hooks for fetching AREA API data
 */

import { useState, useEffect } from 'react';
import type { Action, Reaction, PaginatedResponse, ApiError } from '../types/api';

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8080';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Generic hook for fetching paginated API data
 */
function usePaginatedApi<T>(endpoint: string): UseApiResult<T[]> {
  const [data, setData] = useState<T[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refetchTrigger, setRefetchTrigger] = useState(0);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}${endpoint}`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const json: PaginatedResponse<T> = await response.json();
        
        if (isMounted) {
          setData(json.results);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Unknown error occurred');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [endpoint, refetchTrigger]);

  const refetch = () => setRefetchTrigger(prev => prev + 1);

  return { data, loading, error, refetch };
}

/**
 * Hook for fetching all available actions
 */
export function useActions(): UseApiResult<Action[]> {
  return usePaginatedApi<Action>('/api/actions/');
}

/**
 * Hook for fetching all available reactions
 */
export function useReactions(): UseApiResult<Reaction[]> {
  return usePaginatedApi<Reaction>('/api/reactions/');
}

/**
 * Hook for creating an area
 */
export function useCreateArea() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createArea = async (payload: {
    name: string;
    action: number;
    reaction: number;
    action_config?: Record<string, any>;
    reaction_config?: Record<string, any>;
    status?: 'active' | 'disabled' | 'paused';
  }) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access');
      
      if (!token) {
        throw new Error('Authentication required. Please login.');
      }

      const response = await fetch(`${API_BASE}/api/areas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Session expired. Please login again.');
        }

        const errorData: ApiError = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 
                            Object.values(errorData)[0] || 
                            `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create automation';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createArea, loading, error };
}
