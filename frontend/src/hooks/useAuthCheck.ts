/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** useAuthCheck - Hook to verify authentication status
 */

import { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE, getAccessToken } from '../utils/helper';

interface UseAuthCheckOptions {
  onAuthExpired?: () => void;
  skipCheck?: boolean;
}

/**
 * Hook to verify authentication status on page load
 * Checks if the access token is still valid by calling the backend
 * If invalid, clears localStorage and redirects to login
 */
export const useAuthCheck = (options: UseAuthCheckOptions = {}) => {
  const navigate = useNavigate();
  const { onAuthExpired, skipCheck = false } = options;

  const clearAuthData = useCallback(() => {
    // Clear all authentication data
    localStorage.removeItem('access');
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
  }, []);

  const verifyAuth = useCallback(async () => {
    if (skipCheck) return true;

    const token = getAccessToken();

    // No token means user is not logged in (expected behavior)
    if (!token) {
      return false;
    }

    try {
      // Verify token by calling /auth/me/
      const response = await fetch(`${API_BASE}/auth/me/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        return true;
      }

      // Token is invalid or expired
      if (response.status === 401 || response.status === 403) {
        console.warn('Authentication token is invalid or expired');
        clearAuthData();

        // Call custom callback if provided
        if (onAuthExpired) {
          onAuthExpired();
        }

        // Redirect to login with a message
        navigate('/login?reason=session_expired', { replace: true });
        return false;
      }

      // Other errors (500, network issues, etc.) - don't logout
      console.error('Error verifying authentication:', response.status);
      return true; // Assume still authenticated, might be a server issue
    } catch (error) {
      // Network error - don't logout, might be temporary
      console.error('Network error while verifying authentication:', error);
      return true; // Assume still authenticated
    }
  }, [skipCheck, clearAuthData, onAuthExpired, navigate]);

  useEffect(() => {
    verifyAuth();
  }, [verifyAuth]);

  return { verifyAuth, clearAuthData };
};
