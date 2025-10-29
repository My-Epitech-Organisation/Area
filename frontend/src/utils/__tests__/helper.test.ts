/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** helper tests
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { API_BASE, getStoredUser, getAccessToken, fetchUserData } from '../helper';
import type { User } from '../../types';

describe('helper', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('API_BASE', () => {
    it('should have a default API base URL', () => {
      expect(API_BASE).toBeDefined();
      expect(typeof API_BASE).toBe('string');
    });
  });

  describe('getStoredUser', () => {
    it('should return null when no user is stored', () => {
      const result = getStoredUser();
      expect(result).toBeNull();
    });

    it('should return stored user when valid JSON exists', () => {
      const mockUser: User = {
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      };

      localStorage.setItem('user', JSON.stringify(mockUser));

      const result = getStoredUser();
      expect(result).toEqual(mockUser);
    });

    it('should return null when stored data is invalid JSON', () => {
      localStorage.setItem('user', 'invalid json {');

      const result = getStoredUser();
      expect(result).toBeNull();
    });

    it('should return null when stored data is not an object', () => {
      localStorage.setItem('user', 'just a string');

      const result = getStoredUser();
      expect(result).toBeNull();
    });
  });

  describe('getAccessToken', () => {
    it('should return null when no token is stored', () => {
      const result = getAccessToken();
      expect(result).toBeNull();
    });

    it('should return token from "access" key', () => {
      localStorage.setItem('access', 'token123');

      const result = getAccessToken();
      expect(result).toBe('token123');
    });

    it('should return token from "access_token" key', () => {
      localStorage.setItem('access_token', 'token456');

      const result = getAccessToken();
      expect(result).toBe('token456');
    });

    it('should return token from "token" key', () => {
      localStorage.setItem('token', 'token789');

      const result = getAccessToken();
      expect(result).toBe('token789');
    });

    it('should prioritize "access" over other keys', () => {
      localStorage.setItem('access', 'access-token');
      localStorage.setItem('access_token', 'access_token-token');
      localStorage.setItem('token', 'token-token');

      const result = getAccessToken();
      expect(result).toBe('access-token');
    });
  });

  describe('fetchUserData', () => {
    beforeEach(() => {
      (globalThis as any).fetch = vi.fn();
    });

    it('should return null when no access token exists', async () => {
      const result = await fetchUserData();
      expect(result).toBeNull();
      expect((globalThis as any).fetch).not.toHaveBeenCalled();
    });

    it('should fetch and return user data successfully', async () => {
      localStorage.setItem('access', 'valid-token');

      const mockResponse = {
        id: 1,
        pk: 1,
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      };

      ((globalThis as any).fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await fetchUserData();

      expect((globalThis as any).fetch).toHaveBeenCalledWith(`${API_BASE}/auth/me/`, {
        headers: {
          Authorization: 'Bearer valid-token',
        },
      });

      expect(result).toEqual({
        id: 1,
        name: 'testuser',
        username: 'testuser',
        email: 'test@example.com',
        email_verified: true,
      });

      const storedUser = localStorage.getItem('user');
      expect(storedUser).toBeDefined();
      expect(JSON.parse(storedUser!)).toEqual(result);
    });

    it('should use email as name fallback when username is missing', async () => {
      localStorage.setItem('access', 'valid-token');

      const mockResponse = {
        id: 2,
        email: 'test2@example.com',
        email_verified: false,
      };

      ((globalThis as any).fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await fetchUserData();

      expect(result).toEqual({
        id: 2,
        name: 'test2@example.com',
        username: 'User',
        email: 'test2@example.com',
        email_verified: false,
      });
    });

    it('should use default values when data is missing', async () => {
      localStorage.setItem('access', 'valid-token');

      const mockResponse = {
        pk: 3,
      };

      ((globalThis as any).fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await fetchUserData();

      expect(result).toEqual({
        id: 3,
        name: 'User',
        username: 'User',
        email: '',
        email_verified: false,
      });
    });

    it('should return null when fetch fails', async () => {
      localStorage.setItem('access', 'invalid-token');

      ((globalThis as any).fetch as any).mockResolvedValueOnce({
        ok: false,
        text: async () => 'Unauthorized',
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const result = await fetchUserData();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch user data:', 'Unauthorized');

      consoleSpy.mockRestore();
    });

    it('should return null when fetch throws an error', async () => {
      localStorage.setItem('access', 'valid-token');

      ((globalThis as any).fetch as any).mockRejectedValueOnce(new Error('Network error'));

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const result = await fetchUserData();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching user profile:', expect.any(Error));

      consoleSpy.mockRestore();
    });
  });
});
