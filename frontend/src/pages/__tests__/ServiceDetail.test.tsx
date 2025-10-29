import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ServiceDetail from '../ServiceDetail';
import * as useOAuthHooks from '../../hooks/useOAuth';
import * as useNotificationsHook from '../../hooks/useNotifications';

vi.mock('../../hooks/useOAuth');
vi.mock('../../hooks/useNotifications');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('ServiceDetail Page', () => {
  const mockConnectedServices = [
    {
      service_name: 'github',
      is_expired: false,
      created_at: '2025-01-01',
      expires_at: '2025-12-31',
      expires_in_minutes: 525600,
      has_refresh_token: true,
    },
    {
      service_name: 'google',
      is_expired: false,
      created_at: '2025-01-01',
      expires_at: '2025-12-31',
      expires_in_minutes: 525600,
      has_refresh_token: true,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();

    vi.mocked(useOAuthHooks.useConnectedServices).mockReturnValue({
      services: mockConnectedServices,
      availableProviders: ['github', 'google', 'gmail'],
      loading: false,
      error: null,
      refetch: vi.fn().mockResolvedValue(undefined),
    });

    vi.mocked(useOAuthHooks.useInitiateOAuth).mockReturnValue({
      initiateOAuth: vi.fn().mockResolvedValue(null),
      loading: false,
      error: null,
    });

    vi.mocked(useOAuthHooks.useDisconnectService).mockReturnValue({
      disconnectService: vi.fn().mockResolvedValue(true),
      loading: false,
      error: null,
    });

    vi.mocked(useNotificationsHook.useNotifications).mockReturnValue({
      notifications: [],
      addNotification: vi.fn().mockReturnValue('notif-id'),
      removeNotification: vi.fn(),
      success: vi.fn().mockReturnValue('notif-id'),
      error: vi.fn().mockReturnValue('notif-id'),
      info: vi.fn().mockReturnValue('notif-id'),
      warning: vi.fn().mockReturnValue('notif-id'),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Loading State', () => {
    it('should show loading state initially', () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockImplementation(
        () =>
          new Promise(() => {
          })
      );

      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/loading service details/i)).toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    it('should show error when service not found', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ server: { services: [] } }),
      });

      render(
        <MemoryRouter initialEntries={['/services/unknown']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/service not found/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/back to services/i)).toBeInTheDocument();
    });

    it('should show error when fetch fails', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });

    it('should have link back to services on error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ server: { services: [] } }),
      });

      render(
        <MemoryRouter initialEntries={['/services/unknown']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/service not found/i)).toBeInTheDocument();
      });

      const link = screen.getByText(/back to services/i).closest('a');
      expect(link).toHaveAttribute('href', '/services');
    });
  });

  describe('Service Display', () => {
    const mockGitHubService = {
      id: 1,
      name: 'github',
      logo: 'github_logo.png',
      actions: [
        { name: 'push_event', description: 'Triggered when code is pushed' },
        { name: 'pr_opened', description: 'Triggered when PR is opened' },
      ],
      reactions: [
        { name: 'create_issue', description: 'Creates a new issue' },
      ],
    };

    beforeEach(() => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockGitHubService] },
        }),
      });
    });

    it('should display service name', async () => {
      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/github/i)).toBeInTheDocument();
      });
    });

    it('should display back to services link', async () => {
      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/github/i)).toBeInTheDocument();
      });

      const backLink = screen.getByText(/back to services/i);
      expect(backLink).toBeInTheDocument();
    });

    it('should display service actions', async () => {
      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/triggered when code is pushed/i)).toBeInTheDocument();
      });
    });

    it('should display service reactions', async () => {
      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/creates a new issue/i)).toBeInTheDocument();
      });
    });
  });

  describe('OAuth Connection Status', () => {
    const mockGitHubService = {
      id: 1,
      name: 'github',
      logo: 'github_logo.png',
      actions: [{ name: 'push_event', description: 'Push event' }],
      reactions: [{ name: 'create_issue', description: 'Create issue' }],
    };

    it('should show connected status for connected OAuth service', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockGitHubService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/connected/i)).toBeInTheDocument();
      });
    });

    it('should show connect button for disconnected OAuth service', async () => {
      vi.mocked(useOAuthHooks.useConnectedServices).mockReturnValue({
        services: [],
        availableProviders: ['github', 'google'],
        loading: false,
        error: null,
        refetch: vi.fn().mockResolvedValue(undefined),
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockGitHubService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/connect/i)).toBeInTheDocument();
      });
    });
  });

  describe('Service Identification', () => {
    it('should find service by ID', async () => {
      const mockService = {
        id: 5,
        name: 'test_by_id',
        logo: null,
        actions: [],
        reactions: [],
      };

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/5']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/test_by_id/i)).toBeInTheDocument();
      });
    });

    it('should find service by name', async () => {
      const mockService = {
        id: 6,
        name: 'test_by_name',
        logo: null,
        actions: [],
        reactions: [],
      };

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/test_by_name']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/test_by_name/i)).toBeInTheDocument();
      });
    });
  });

  describe('Logo Display', () => {
    it('should display service logo when available', async () => {
      const mockService = {
        id: 7,
        name: 'github',
        logo: 'https://example.com/github.png',
        actions: [],
        reactions: [],
      };

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/github']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        const logo = screen.getByAltText(/github logo/i);
        expect(logo).toBeInTheDocument();
      });
    });

    it('should show fallback when logo not available', async () => {
      const mockService = {
        id: 8,
        name: 'testservice',
        logo: null,
        actions: [],
        reactions: [],
      };

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          server: { services: [mockService] },
        }),
      });

      render(
        <MemoryRouter initialEntries={['/services/testservice']}>
          <Routes>
            <Route path="/services/:serviceId" element={<ServiceDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('T')).toBeInTheDocument();
      });
    });
  });
});
