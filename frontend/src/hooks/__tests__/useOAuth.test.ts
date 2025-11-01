/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** useOAuth tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import {
  useConnectedServices,
  useInitiateOAuth,
  useDisconnectService,
  useIsServiceConnected,
} from '../useOAuth';
import { API_BASE } from '../../utils/helper';

describe('useOAuth', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    (globalThis as any).fetch = vi.fn();
  });

  describe('useConnectedServices', () => {
    it('should initialize with loading state', () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockImplementation(() => new Promise(() => {}));

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useConnectedServices());

      expect(result.current.loading).toBe(true);
      expect(result.current.services).toEqual([]);
      expect(result.current.availableProviders).toEqual([]);
    });

    it('should fetch connected services successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockData = {
        connected_services: [
          {
            id: 1,
            service_name: 'google',
            display_name: 'Google',
            connected_at: '2024-01-01T00:00:00Z',
            is_expired: false,
            expires_in_minutes: null,
            has_refresh_token: true,
          },
        ],
        available_providers: ['google', 'github', 'discord'],
        total_connected: 1,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useConnectedServices());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.services).toEqual(mockData.connected_services);
      expect(result.current.availableProviders).toEqual(mockData.available_providers);
      expect(result.current.error).toBeNull();

      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/auth/services/`, {
        headers: {
          Authorization: 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });
    });

    it('should handle fetch error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Unauthorized',
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useConnectedServices());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.services).toEqual([]);
    });

    it('should handle missing token', async () => {
      const { result } = renderHook(() => useConnectedServices());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toContain('No authentication token');
    });

    it('should provide refetch function', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          connected_services: [],
          available_providers: [],
          total_connected: 0,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useConnectedServices());

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

  describe('useInitiateOAuth', () => {
    it('should initialize with no loading state', () => {
      const { result } = renderHook(() => useInitiateOAuth());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should initiate OAuth flow successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      const mockResponse = {
        redirect_url: 'https://oauth.google.com/authorize?state=abc',
        state: 'abc',
        provider: 'google',
        expires_in: 600,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      localStorage.setItem('access', 'test-token');

      delete (window as any).location;
      (window as any).location = { href: '' };

      const { result } = renderHook(() => useInitiateOAuth());

      let response;
      await act(async () => {
        response = await result.current.initiateOAuth('google');
      });

      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/auth/oauth/google/`, {
        headers: {
          Authorization: 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });

      expect(response).toEqual(mockResponse);
      expect(window.location.href).toBe(mockResponse.redirect_url);
    });

    it('should handle initiate OAuth error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request',
        json: async () => ({ message: 'Invalid provider' }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useInitiateOAuth());

      let response;
      await act(async () => {
        response = await result.current.initiateOAuth('invalid');
      });

      expect(response).toBeNull();
      expect(result.current.error).toContain('Invalid provider');
    });

    it('should handle missing token', async () => {
      const { result } = renderHook(() => useInitiateOAuth());

      let response;
      await act(async () => {
        response = await result.current.initiateOAuth('google');
      });

      expect(response).toBeNull();
      expect(result.current.error).toContain('No authentication token');
    });
  });

  describe('useDisconnectService', () => {
    it('should initialize with no loading state', () => {
      const { result } = renderHook(() => useDisconnectService());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should disconnect service successfully', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Service disconnected' }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDisconnectService());

      let success;
      await act(async () => {
        success = await result.current.disconnectService('google');
      });

      expect(success).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/auth/services/google/disconnect/`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });
    });

    it('should handle disconnect error', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
        json: async () => ({ message: 'Service not found' }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useDisconnectService());

      let success;
      await act(async () => {
        success = await result.current.disconnectService('unknown');
      });

      expect(success).toBe(false);
      expect(result.current.error).toContain('Service not found');
    });

    it('should handle missing token', async () => {
      const { result } = renderHook(() => useDisconnectService());

      let success;
      await act(async () => {
        success = await result.current.disconnectService('google');
      });

      expect(success).toBe(false);
      expect(result.current.error).toContain('No authentication token');
    });
  });

  describe('useIsServiceConnected', () => {
    it('should return false when loading', () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useIsServiceConnected('google'));

      expect(result.current).toBe(false);
    });

    it('should return true for connected service', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          connected_services: [
            {
              id: 1,
              service_name: 'Google',
              display_name: 'Google',
              connected_at: '2024-01-01T00:00:00Z',
              is_expired: false,
              expires_in_minutes: null,
              has_refresh_token: true,
            },
          ],
          available_providers: ['google'],
          total_connected: 1,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useIsServiceConnected('google'));

      await waitFor(() => {
        expect(result.current).toBe(true);
      });
    });

    it('should return false for non-connected service', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          connected_services: [],
          available_providers: ['google'],
          total_connected: 0,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useIsServiceConnected('google'));

      await waitFor(() => {
        expect(result.current).toBe(false);
      });
    });

    it('should return false for expired service', async () => {
      const mockFetch = (globalThis as any).fetch as any;
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          connected_services: [
            {
              id: 1,
              service_name: 'Google',
              display_name: 'Google',
              connected_at: '2024-01-01T00:00:00Z',
              is_expired: true,
              expires_in_minutes: null,
              has_refresh_token: false,
            },
          ],
          available_providers: ['google'],
          total_connected: 1,
        }),
      });

      localStorage.setItem('access', 'test-token');

      const { result } = renderHook(() => useIsServiceConnected('google'));

      await waitFor(() => {
        expect(result.current).toBe(false);
      });
    });
  });
});
