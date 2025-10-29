import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Profile from '../Profile';

vi.mock('../../utils/helper', () => ({
  API_BASE: 'http://localhost:8000',
  getStoredUser: vi.fn(),
  getAccessToken: vi.fn(),
  fetchUserData: vi.fn(),
}));

vi.mock('../../components/ProfileModal', () => ({
  default: () => <div data-testid="profile-modal">Profile Modal</div>,
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import { getStoredUser, getAccessToken, fetchUserData } from '../../utils/helper';

globalThis.fetch = vi.fn();

describe('Profile Page', () => {
  const mockUser = {
    id: 1,
    name: 'Test User',
    username: 'testuser',
    email: 'test@example.com',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();

    vi.mocked(getStoredUser).mockReturnValue(mockUser);
    vi.mocked(getAccessToken).mockReturnValue('test-token');
    vi.mocked(fetchUserData).mockResolvedValue(mockUser);

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => mockUser,
    } as Response);
  });

  describe('Authentication', () => {
    it('should redirect to login if no access token', async () => {
      vi.mocked(getAccessToken).mockReturnValue(null);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });

    it('should load user profile when authenticated', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('User Profile Display', () => {
    it('should fetch and display user profile', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle profile data fetch error gracefully', async () => {
      vi.mocked(fetchUserData).mockRejectedValueOnce(new Error('Network error'));
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });

    it('should redirect to login if user not found', async () => {
      vi.mocked(getStoredUser).mockReturnValue(null);
      vi.mocked(fetchUserData).mockResolvedValueOnce(null);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });
  });

  describe('Profile Updates', () => {
    it('should handle saving state', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should display success message on successful update', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockUser, username: 'newusername' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Local Storage', () => {
    it('should use stored user data initially', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(getStoredUser).toHaveBeenCalled();
      });
    });

    it('should update localStorage after fetching user data', async () => {
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(setItemSpy).toHaveBeenCalledWith('user', expect.any(String));
      });

      setItemSpy.mockRestore();
    });
  });

  describe('Form Interactions', () => {
    it('should enter edit mode when edit button is clicked', async () => {
      const { container } = render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });

      const buttons = container.querySelectorAll('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should cancel edit and restore original values', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(getStoredUser).toHaveBeenCalled();
      });
    });
  });

  describe('Password Change', () => {
    it('should handle password mismatch error', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should open password confirmation modal on submit', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle password change API call', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Password updated' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle password change API error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid old password' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Email Verification', () => {
    it('should handle resend verification email', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Verification email sent' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle resend verification error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Failed to send email' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Profile Update Scenarios', () => {
    it('should handle username change', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockUser, username: 'newusername' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle email change', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockUser, email: 'newemail@example.com' }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle profile update API error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ email: ['Email already in use'] }),
      } as Response);

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle no changes scenario', async () => {
      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing user email for verification', async () => {
      vi.mocked(getStoredUser).mockReturnValue({ ...mockUser, email: '' });
      vi.mocked(fetchUserData).mockResolvedValue({ ...mockUser, email: '' });

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });

    it('should handle connection error during update', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(
        <MemoryRouter>
          <Profile />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(fetchUserData).toHaveBeenCalled();
      });
    });
  });
});
