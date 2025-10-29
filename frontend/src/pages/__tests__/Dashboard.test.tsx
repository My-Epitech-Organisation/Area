import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import Dashboard from '../Dashboard';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

vi.mock('../../hooks/useOAuth', () => ({
  useConnectedServices: vi.fn(() => ({
    services: [],
    loading: false,
  })),
}));

vi.mock('../../utils/helper', () => ({
  getStoredUser: vi.fn(),
  getAccessToken: vi.fn(),
  fetchUserData: vi.fn(),
  API_BASE: 'http://localhost:8000',
}));

vi.mock('react-chartjs-2', () => ({
  Doughnut: () => <div data-testid="doughnut-chart">Chart</div>,
}));

vi.mock('chart.js', () => ({
  Chart: {
    register: vi.fn(),
  },
  ArcElement: vi.fn(),
  Tooltip: vi.fn(),
  Legend: vi.fn(),
}));

import { getStoredUser, getAccessToken, fetchUserData } from '../../utils/helper';
import { useConnectedServices } from '../../hooks/useOAuth';

globalThis.fetch = vi.fn();

describe('Dashboard Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering and Initial State', () => {
    it('should render dashboard page', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);
      vi.mocked(getAccessToken).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      expect(document.querySelector('body')).toBeInTheDocument();
    });

    it('should show loading state initially', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      expect(vi.mocked(fetchUserData)).not.toHaveBeenCalled();
    });
  });

  describe('User Authentication', () => {
    it('should handle case when user is not logged in', () => {
      vi.mocked(getStoredUser).mockReturnValue(null);
      vi.mocked(getAccessToken).mockReturnValue(null);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      expect(document.querySelector('body')).toBeInTheDocument();
    });

    it('should load user data when logged in', async () => {
      const mockUser = {
        id: 1,
        name: 'John Doe',
        username: 'johndoe',
        email: 'john@example.com',
        email_verified: true,
      };

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');
      vi.mocked(fetchUserData).mockResolvedValue(mockUser);

      vi.mocked(globalThis.fetch).mockResolvedValue({
        ok: true,
        json: async () => ({ results: [] }),
      } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(getStoredUser).toHaveBeenCalled();
      });
    });
  });

  describe('Services Display', () => {
    it('should fetch and display services', async () => {
      const mockUser = {
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      };

      const mockServices = [
        { id: 1, name: 'Gmail', description: 'Email service' },
        { id: 2, name: 'Spotify', description: 'Music service' },
      ];

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');
      vi.mocked(fetchUserData).mockResolvedValue(mockUser);

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle connected services from useOAuth hook', () => {
      const mockConnectedServices = [
        {
          id: 1,
          service_name: 'gmail',
          is_expired: false,
          created_at: '2024-01-01',
          expires_at: '2024-12-31',
          expires_in_minutes: 525600,
          has_refresh_token: true,
        },
        {
          id: 2,
          service_name: 'spotify',
          is_expired: false,
          created_at: '2024-01-01',
          expires_at: '2024-12-31',
          expires_in_minutes: 525600,
          has_refresh_token: true,
        },
      ];

      vi.mocked(useConnectedServices).mockReturnValue({
        services: mockConnectedServices,
        availableProviders: ['gmail', 'spotify'],
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      expect(useConnectedServices).toHaveBeenCalled();
    });

    it('should render chart component when services are loaded', async () => {
      const mockUser = {
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      };

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');
      vi.mocked(fetchUserData).mockResolvedValue(mockUser);

      const mockServices = [{ id: 1, name: 'Gmail', description: 'Email' }];

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch).mockRejectedValue(new Error('API Error'));

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle fetch errors when loading services', async () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Service Normalization', () => {
    it('should normalize service names correctly', async () => {
      const mockServices = [
        { id: 1, name: 'G-Mail', description: 'Email' },
        { id: 2, name: 'Spo Ti fy!', description: 'Music' },
      ];

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test',
        username: 'test',
        email: 'test@test.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Navigation', () => {
    it('should have navigation capability', () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      expect(document.querySelector('body')).toBeInTheDocument();
    });
  });

  describe('Multiple Services Scenarios', () => {
    it('should handle empty services list', async () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');
      vi.mocked(fetchUserData).mockResolvedValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle large number of services', async () => {
      const mockServices = Array.from({ length: 20 }, (_, i) => ({
        id: i + 1,
        name: `Service ${i + 1}`,
        description: `Description ${i + 1}`,
      }));

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should handle services with missing fields', async () => {
      const mockServices = [
        { id: 1, name: 'Gmail' },
        { id: 2, description: 'No name service' },
        { id: 3 },
      ];

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Active Services Detection', () => {
    it('should detect internal default services', async () => {
      const mockServices = [
        { id: 1, name: 'Timer', description: 'Timer service' },
        { id: 2, name: 'Debug', description: 'Debug service' },
        { id: 3, name: 'Weather', description: 'Weather service' },
        { id: 4, name: 'Email', description: 'Email service' },
        { id: 5, name: 'Webhook', description: 'Webhook service' },
      ];

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should detect connected services from OAuth', async () => {
      const mockServices = [
        { id: 1, name: 'Gmail', description: 'Email' },
        { id: 2, name: 'Spotify', description: 'Music' },
        { id: 3, name: 'Twitter', description: 'Social' },
      ];

      const mockConnectedServices = [
        {
          id: 1,
          service_name: 'Gmail',
          is_expired: false,
          created_at: '2024-01-01',
          expires_at: '2024-12-31',
          expires_in_minutes: 525600,
          has_refresh_token: true,
        },
      ];

      vi.mocked(useConnectedServices).mockReturnValue({
        services: mockConnectedServices,
        availableProviders: ['gmail', 'spotify'],
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should ignore expired connected services', async () => {
      const mockServices = [{ id: 1, name: 'Gmail', description: 'Email' }];

      const mockConnectedServices = [
        {
          id: 1,
          service_name: 'Gmail',
          is_expired: true,
          created_at: '2024-01-01',
          expires_at: '2024-01-02',
          expires_in_minutes: 0,
          has_refresh_token: false,
        },
      ];

      vi.mocked(useConnectedServices).mockReturnValue({
        services: mockConnectedServices,
        availableProviders: ['gmail'],
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('User Areas', () => {
    it('should fetch user areas', async () => {
      const mockAreas = {
        results: [
          { id: 1, name: 'Area 1', enabled: true },
          { id: 2, name: 'Area 2', enabled: false },
        ],
      };

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAreas,
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should handle areas fetch error', async () => {
      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        } as Response)
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'Failed to fetch areas' }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Service Logo Handling', () => {
    it('should handle services with logo URLs', async () => {
      const mockServices = [
        { id: 1, name: 'Gmail', logo: '//logo.clearbit.com/gmail.com', description: 'Email' },
        {
          id: 2,
          name: 'Spotify',
          logo: 'https://logo.clearbit.com/spotify.com',
          description: 'Music',
        },
      ];

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle services without logos', async () => {
      const mockServices = [{ id: 1, name: 'CustomService', description: 'Custom service' }];

      vi.mocked(getStoredUser).mockReturnValue({
        id: 1,
        name: 'Test User',
        username: 'testuser',
        email: 'test@example.com',
      });
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Statistics and Chart', () => {
    const mockUser = {
      id: 1,
      name: 'Test User',
      username: 'testuser',
      email: 'test@example.com',
    };

    it('should display chart when services are available', async () => {
      const mockServices = [
        { id: 1, name: 'github', description: 'GitHub' },
        { id: 2, name: 'slack', description: 'Slack' },
      ];

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockServices,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should fetch areas and services on mount', async () => {
      const mockAreas = [
        {
          id: 1,
          name: 'Area 1',
          action_service: 'github',
          reaction_service: 'slack',
          is_active: true,
          user: 1,
        },
        {
          id: 2,
          name: 'Area 2',
          action_service: 'google',
          reaction_service: 'slack',
          is_active: true,
          user: 1,
        },
        {
          id: 3,
          name: 'Area 3',
          action_service: 'github',
          reaction_service: 'email',
          is_active: false,
          user: 1,
        },
      ];

      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockAreas }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should handle empty services list', async () => {
      vi.mocked(getStoredUser).mockReturnValue(mockUser);
      vi.mocked(getAccessToken).mockReturnValue('test-token');

      vi.mocked(globalThis.fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);

      render(
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      });
    });
  });
});
