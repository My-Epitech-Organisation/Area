/**
 * Debug API Service Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { triggerDebugAction, getDebugExecutions } from '../debugApi';

globalThis.fetch = vi.fn();

describe('debugApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('triggerDebugAction', () => {
    it('should successfully trigger debug action', async () => {
      const mockResponse = {
        success: true,
        message: 'Debug action triggered',
        execution_id: 123,
      };

      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await triggerDebugAction(1);

      expect(result).toEqual(mockResponse);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/debug/trigger/1/'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should throw error when no token is present', async () => {
      await expect(triggerDebugAction(1)).rejects.toThrow('Authentication required');
    });

    it('should throw error when API returns error response', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ error: 'Area not found' }),
      });

      await expect(triggerDebugAction(1)).rejects.toThrow('Area not found');
    });

    it('should throw error with status text when error response has no message', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({}),
      });

      await expect(triggerDebugAction(1)).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('should handle JSON parsing error in error response', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(triggerDebugAction(1)).rejects.toThrow('HTTP 500: Internal Server Error');
    });
  });

  describe('getDebugExecutions', () => {
    it('should successfully get debug executions', async () => {
      const mockResponse = {
        executions: [
          {
            id: 1,
            status: 'success',
            triggered_at: '2025-10-29T10:00:00Z',
          },
          {
            id: 2,
            status: 'failure',
            triggered_at: '2025-10-29T09:00:00Z',
          },
        ],
      };

      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getDebugExecutions(1);

      expect(result).toEqual(mockResponse);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/debug/executions/1/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should throw error when no token is present', async () => {
      await expect(getDebugExecutions(1)).rejects.toThrow('Authentication required');
    });

    it('should throw error when API returns error response', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden',
        json: async () => ({ error: 'Access denied' }),
      });

      await expect(getDebugExecutions(1)).rejects.toThrow('Access denied');
    });

    it('should throw error with status text when error response has no message', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({}),
      });

      await expect(getDebugExecutions(1)).rejects.toThrow('HTTP 404: Not Found');
    });

    it('should handle JSON parsing error in error response', async () => {
      localStorage.setItem('access', 'test-token');

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(getDebugExecutions(1)).rejects.toThrow('HTTP 500: Internal Server Error');
    });
  });
});
