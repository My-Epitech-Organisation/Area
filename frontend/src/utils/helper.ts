/*
 ** EPITECH PROJECT, 2025
 ** Area
 ** File description:
 ** helper
 */

import type { User } from '../types';

export const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8080';

export const getStoredUser = (): User | null => {
  const stored = localStorage.getItem('user');
  if (!stored) return null;
  try {
    return JSON.parse(stored) as User;
  } catch {
    return null;
  }
};

export const getAccessToken = (): string | null => {
  const token =
    localStorage.getItem('access') ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('token');
  return token;
};

export const fetchUserData = async (): Promise<User | null> => {
  const accessToken = getAccessToken();

  if (!accessToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE}/auth/me/`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (response.ok) {
      const userData = await response.json();
      const user: User = {
        name: userData.username || userData.email || 'User',
        username: userData.username || 'User',
        email: userData.email || '',
        id: userData.id || userData.pk,
        email_verified: userData.email_verified || false,
      };

      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } else {
      console.error('Failed to fetch user data:', await response.text());
      return null;
    }
  } catch (err) {
    console.error('Error fetching user profile:', err);
    return null;
  }
};
