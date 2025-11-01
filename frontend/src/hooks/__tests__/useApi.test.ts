/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** useApi tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import {
  useActions,
  useReactions,
  useAreas,
  useCreateArea,
  useUpdateArea,
  useDeleteArea,
} from '../useApi';
import { API_BASE } from '../../utils/helper';

describe('useApi', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    (globalThis as any).fetch = vi.fn();
  });

  describe('useActions', () => {
    it('should fetch actions successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockActions = [
        {
          id: 1,
          service: 1,
          name: 'timer_daily',
          description: 'Daily timer',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockActions,
          next: null,
          count: 1,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useActions());

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockActions);
      expect(result.current.error).toBeNull();
      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/actions/`, {
        headers: {
          Authorization: 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });
    });

    it('should handle error when fetching actions', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useActions());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeTruthy();
    });

    it('should fetch paginated results', async () => {
      const mockFetch = (globalThis as any).fetch as any;

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [{ id: 1, service: 1, name: 'action1', description: 'Action 1' }],
          next: `${API_BASE}/api/actions/?page=2`,
          count: 2,
        }),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [{ id: 2, service: 1, name: 'action2', description: 'Action 2' }],
          next: null,
          count: 2,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useActions());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toHaveLength(2);
      expect(result.current.data?.[0].id).toBe(1);
      expect(result.current.data?.[1].id).toBe(2);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('useReactions', () => {
    it('should fetch reactions successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockReactions = [
        {
          id: 1,
          service: 1,
          name: 'send_email',
          description: 'Send email',
          config_schema: { type: 'object', properties: {} },
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockReactions,
          next: null,
          count: 1,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useReactions());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockReactions);
      expect(result.current.error).toBeNull();
    });

    it('should handle error when fetching reactions', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useReactions());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toContain('Network error');
    });
  });

  describe('useAreas', () => {
    it('should fetch areas successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockAreas = [
        {
          id: 1,
          owner: 1,
          name: 'Test Area',
          action: 1,
          reaction: 1,
          action_config: {},
          reaction_config: {},
          status: 'active' as const,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: mockAreas,
          next: null,
          count: 1,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useAreas());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockAreas);
      expect(result.current.error).toBeNull();
    });

    it('should handle 401 error with proper message', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useAreas());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toContain('Session expired');
    });

    it('should work without token', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          results: [],
          next: null,
          count: 0,
        }),
      });

      const { result } = renderHook(() => useAreas());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/areas/`, {
        headers: {
          Authorization: '',
          'Content-Type': 'application/json',
        },
      });
    });

    it('should trigger refetch when refetch is called', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          results: [],
          next: null,
          count: 0,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useAreas());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockFetch).toHaveBeenCalledTimes(1);

      act(() => {
        result.current.refetch();
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('useCreateArea', () => {
    it('should initialize with no loading state', () => {
      const { result } = renderHook(() => useCreateArea());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should create area successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockArea = {
        id: 1,
        owner: 1,
        name: 'Test Area',
        action: 1,
        reaction: 2,
        action_config: { param: 'value' },
        reaction_config: { param: 'value' },
        status: 'active' as const,
        created_at: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockArea,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useCreateArea());

      let createdArea;
      await act(async () => {
        createdArea = await result.current.createArea({
          name: 'Test Area',
          action: 1,
          reaction: 2,
          action_config: { param: 'value' },
          reaction_config: { param: 'value' },
          status: 'active',
        });
      });

      expect(createdArea).toEqual(mockArea);
      expect(result.current.error).toBeNull();
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/areas/`,
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
        })
      );
    });

    it('should handle missing token error', async () => {
      const { result } = renderHook(() => useCreateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.createArea({
            name: 'Test',
            action: 1,
            reaction: 2,
          });
        });
      }).rejects.toThrow('Authentication required');
    });

    it('should handle 401 error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useCreateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.createArea({
            name: 'Test',
            action: 1,
            reaction: 2,
          });
        });
      }).rejects.toThrow('Session expired');
    });

    it('should handle validation errors from API', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({
          name: ['This field is required'],
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useCreateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.createArea({
            name: '',
            action: 1,
            reaction: 2,
          });
        });
      }).rejects.toThrow('This field is required');
    });

    it('should handle API error with detail', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({
          detail: 'Invalid configuration',
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useCreateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.createArea({
            name: 'Test',
            action: 1,
            reaction: 2,
          });
        });
      }).rejects.toThrow('Invalid configuration');
    });
  });

  describe('useUpdateArea', () => {
    it('should initialize with no loading state', () => {
      const { result } = renderHook(() => useUpdateArea());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should update area successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const updatedArea = {
        id: 1,
        owner: 1,
        name: 'Updated Area',
        action: 1,
        reaction: 2,
        action_config: {},
        reaction_config: {},
        status: 'paused' as const,
        created_at: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => updatedArea,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useUpdateArea());

      let updated;
      await act(async () => {
        updated = await result.current.updateArea(1, {
          name: 'Updated Area',
          status: 'paused',
        });
      });

      expect(updated).toEqual(updatedArea);
      expect(result.current.error).toBeNull();
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/areas/1/`,
        expect.objectContaining({
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
        })
      );
    });

    it('should handle missing token error', async () => {
      const { result } = renderHook(() => useUpdateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.updateArea(1, { name: 'Test' });
        });
      }).rejects.toThrow('Authentication required');
    });

    it('should handle 401 error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useUpdateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.updateArea(1, { name: 'Test' });
        });
      }).rejects.toThrow('Session expired');
    });

    it('should handle API errors', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({
          detail: 'Area not found',
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useUpdateArea());

      await expect(async () => {
        await act(async () => {
          await result.current.updateArea(999, { name: 'Test' });
        });
      }).rejects.toThrow('Area not found');
    });
  });

  describe('useDeleteArea', () => {
    it('should initialize with no loading state', () => {
      const { result } = renderHook(() => useDeleteArea());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should delete area successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDeleteArea());

      let deleted;
      await act(async () => {
        deleted = await result.current.deleteArea(1);
      });

      expect(deleted).toBe(true);
      expect(result.current.error).toBeNull();
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/areas/1/`,
        expect.objectContaining({
          method: 'DELETE',
          headers: {
            Authorization: 'Bearer test-token',
          },
        })
      );
    });

    it('should handle missing token error', async () => {
      const { result } = renderHook(() => useDeleteArea());

      await expect(async () => {
        await act(async () => {
          await result.current.deleteArea(1);
        });
      }).rejects.toThrow('Authentication required');
    });

    it('should handle 401 error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDeleteArea());

      await expect(async () => {
        await act(async () => {
          await result.current.deleteArea(1);
        });
      }).rejects.toThrow('Session expired');
    });

    it('should handle API errors with detail', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({
          detail: 'Area not found',
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDeleteArea());

      await expect(async () => {
        await act(async () => {
          await result.current.deleteArea(999);
        });
      }).rejects.toThrow('Area not found');
    });

    it('should handle API errors without detail', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({}),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDeleteArea());

      await expect(async () => {
        await act(async () => {
          await result.current.deleteArea(1);
        });
      }).rejects.toThrow('HTTP 500');
    });
  });
});
