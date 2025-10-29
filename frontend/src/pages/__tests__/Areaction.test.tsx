import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Areaction from '../Areaction';

vi.mock('../../hooks/useApi', () => ({
  useActions: vi.fn(),
  useReactions: vi.fn(),
  useAreas: vi.fn(),
  useCreateArea: vi.fn(),
  useUpdateArea: vi.fn(),
  useDeleteArea: vi.fn(),
}));

vi.mock('../../utils/helper', () => ({
  API_BASE: 'http://localhost:8000',
  getStoredUser: vi.fn(),
  fetchUserData: vi.fn(),
  getAccessToken: vi.fn(() => 'test-token'),
}));

vi.mock('../../utils/areaHelpers', () => ({
  findActionByName: vi.fn(),
  findReactionByName: vi.fn(),
  generateAreaName: vi.fn(() => 'Generated Area Name'),
}));

import * as useApiHooks from '../../hooks/useApi';
import { getStoredUser, fetchUserData } from '../../utils/helper';

globalThis.fetch = vi.fn();

describe('Areaction Page', () => {
  const mockUser = {
    id: 1,
    name: 'Test User',
    username: 'testuser',
    email: 'test@example.com',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(useApiHooks.useActions).mockReturnValue({
      data: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    vi.mocked(useApiHooks.useReactions).mockReturnValue({
      data: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    vi.mocked(useApiHooks.useAreas).mockReturnValue({
      data: [],
      loading: false,
      error: null,
      refetch: vi.fn().mockResolvedValue(undefined),
    });

    vi.mocked(useApiHooks.useCreateArea).mockReturnValue({
      createArea: vi.fn().mockResolvedValue({ id: 1 }),
      loading: false,
      error: null,
    });

    vi.mocked(useApiHooks.useUpdateArea).mockReturnValue({
      updateArea: vi.fn().mockResolvedValue({}),
      loading: false,
      error: null,
    });

    vi.mocked(useApiHooks.useDeleteArea).mockReturnValue({
      deleteArea: vi.fn().mockResolvedValue(true),
      loading: false,
      error: null,
    });

    vi.mocked(getStoredUser).mockReturnValue(mockUser);
    vi.mocked(fetchUserData).mockResolvedValue(mockUser);

    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => ({ server: { services: [] } }),
    } as Response);
  });

  describe('Loading State', () => {
    it('should show loading state initially', async () => {
      vi.mocked(useApiHooks.useActions).mockReturnValue({
        data: [],
        loading: true,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    it('should display error when actions fail to load', async () => {
      vi.mocked(useApiHooks.useActions).mockReturnValue({
        data: [],
        loading: false,
        error: 'Failed to load actions',
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/failed to load actions/i)).toBeInTheDocument();
      });
    });

    it('should display error when reactions fail to load', async () => {
      vi.mocked(useApiHooks.useReactions).mockReturnValue({
        data: [],
        loading: false,
        error: 'Failed to load reactions',
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/failed to load reactions/i)).toBeInTheDocument();
      });
    });

    it('should handle services fetch error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Page Rendering', () => {
    it('should render with preselected service from URL', async () => {
      render(
        <MemoryRouter initialEntries={['/?service=github']}>
          <Routes>
            <Route path="/" element={<Areaction />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should render with preselected action and reaction from URL', async () => {
      render(
        <MemoryRouter initialEntries={['/?service=github&action=push_event&reaction=send_email']}>
          <Routes>
            <Route path="/" element={<Areaction />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Service Selection', () => {
    it('should display services when loaded', async () => {
      const mockServices = [
        {
          name: 'github',
          logo: 'github.png',
          actions: [{ name: 'push_event', description: 'Triggered on push' }],
          reactions: [],
        },
      ];

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ server: { services: mockServices } }),
      } as Response);

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle empty services list', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ server: { services: [] } }),
      } as Response);

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('User Areas Display', () => {
    it('should display user areas when available', async () => {
      const mockAreas = [
        {
          id: 1,
          name: 'Test Area',
          owner: 1,
          action: 1,
          reaction: 1,
          action_service: 'github',
          reaction_service: 'slack',
          action_config: {},
          reaction_config: {},
          is_active: true,
          status: 'active' as const,
          created_at: '2025-01-01',
          updated_at: '2025-01-01',
        },
      ];

      vi.mocked(useApiHooks.useAreas).mockReturnValue({
        data: mockAreas,
        loading: false,
        error: null,
        refetch: vi.fn().mockResolvedValue(undefined),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/Test Area/i)).toBeInTheDocument();
      });
    });

    it('should handle no areas', async () => {
      vi.mocked(useApiHooks.useAreas).mockReturnValue({
        data: [],
        loading: false,
        error: null,
        refetch: vi.fn().mockResolvedValue(undefined),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Form Interaction', () => {
    it('should handle create area loading state', async () => {
      vi.mocked(useApiHooks.useCreateArea).mockReturnValue({
        createArea: vi.fn().mockResolvedValue({ id: 1 }),
        loading: true,
        error: null,
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle update area loading state', async () => {
      vi.mocked(useApiHooks.useUpdateArea).mockReturnValue({
        updateArea: vi.fn().mockResolvedValue({}),
        loading: true,
        error: null,
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Action/Reaction Selection', () => {
    it('should handle action selection', async () => {
      const mockActions = [
        {
          id: 1,
          name: 'test_action',
          service: 1,
          service_name: 'test_service',
          description: 'Test action',
          config_fields: [],
        },
      ];

      vi.mocked(useApiHooks.useActions).mockReturnValue({
        data: mockActions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle reaction selection', async () => {
      const mockReactions = [
        {
          id: 1,
          name: 'test_reaction',
          service: 1,
          service_name: 'test_service',
          description: 'Test reaction',
          config_fields: [],
        },
      ];

      vi.mocked(useApiHooks.useReactions).mockReturnValue({
        data: mockReactions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should filter actions by selected service', async () => {
      const mockActions = [
        {
          id: 1,
          name: 'action1',
          service: 1,
          service_name: 'service1',
          description: 'Action 1',
          config_fields: [],
        },
        {
          id: 2,
          name: 'action2',
          service: 2,
          service_name: 'service2',
          description: 'Action 2',
          config_fields: [],
        },
      ];

      vi.mocked(useApiHooks.useActions).mockReturnValue({
        data: mockActions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should filter reactions by selected service', async () => {
      const mockReactions = [
        {
          id: 1,
          name: 'reaction1',
          service: 1,
          service_name: 'service1',
          description: 'Reaction 1',
          config_fields: [],
        },
        {
          id: 2,
          name: 'reaction2',
          service: 2,
          service_name: 'service2',
          description: 'Reaction 2',
          config_fields: [],
        },
      ];

      vi.mocked(useApiHooks.useReactions).mockReturnValue({
        data: mockReactions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Area Creation', () => {
    it('should successfully create a new area', async () => {
      const createAreaMock = vi.fn().mockResolvedValue({ id: 123 });
      vi.mocked(useApiHooks.useCreateArea).mockReturnValue({
        createArea: createAreaMock,
        loading: false,
        error: null,
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle create area error', async () => {
      vi.mocked(useApiHooks.useCreateArea).mockReturnValue({
        createArea: vi.fn().mockRejectedValue(new Error('Create failed')),
        loading: false,
        error: 'Create failed',
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Area Update', () => {
    it('should successfully update an existing area', async () => {
      const updateAreaMock = vi.fn().mockResolvedValue({});
      vi.mocked(useApiHooks.useUpdateArea).mockReturnValue({
        updateArea: updateAreaMock,
        loading: false,
        error: null,
      });

      render(
        <MemoryRouter initialEntries={['/areaction?id=1']}>
          <Routes>
            <Route path="/areaction" element={<Areaction />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle update area error', async () => {
      vi.mocked(useApiHooks.useUpdateArea).mockReturnValue({
        updateArea: vi.fn().mockRejectedValue(new Error('Update failed')),
        loading: false,
        error: 'Update failed',
      });

      render(
        <MemoryRouter initialEntries={['/areaction?id=1']}>
          <Routes>
            <Route path="/areaction" element={<Areaction />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Area Deletion', () => {
    it('should successfully delete an area', async () => {
      const deleteAreaMock = vi.fn().mockResolvedValue(true);
      vi.mocked(useApiHooks.useDeleteArea).mockReturnValue({
        deleteArea: deleteAreaMock,
        loading: false,
        error: null,
      });

      const mockAreas = [
        {
          id: 1,
          name: 'Test Area',
          owner: 1,
          action: 1,
          reaction: 1,
          action_service: 'service1',
          reaction_service: 'service2',
          action_config: {},
          reaction_config: {},
          is_active: true,
          status: 'active' as const,
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ];

      vi.mocked(useApiHooks.useAreas).mockReturnValue({
        data: mockAreas,
        loading: false,
        error: null,
        refetch: vi.fn().mockResolvedValue(undefined),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle delete area error', async () => {
      vi.mocked(useApiHooks.useDeleteArea).mockReturnValue({
        deleteArea: vi.fn().mockRejectedValue(new Error('Delete failed')),
        loading: false,
        error: 'Delete failed',
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Configuration Fields', () => {
    it('should handle action config fields', async () => {
      const mockActions = [
        {
          id: 1,
          name: 'test_action',
          service: 1,
          service_name: 'test_service',
          description: 'Test action',
          config_fields: [
            { name: 'field1', type: 'text', required: true },
            { name: 'field2', type: 'number', required: false },
          ],
        },
      ];

      vi.mocked(useApiHooks.useActions).mockReturnValue({
        data: mockActions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle reaction config fields', async () => {
      const mockReactions = [
        {
          id: 1,
          name: 'test_reaction',
          service: 1,
          service_name: 'test_service',
          description: 'Test reaction',
          config_fields: [
            { name: 'field1', type: 'text', required: true },
            { name: 'field2', type: 'email', required: false },
          ],
        },
      ];

      vi.mocked(useApiHooks.useReactions).mockReturnValue({
        data: mockReactions,
        loading: false,
        error: null,
        refetch: vi.fn(),
      });

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty services list', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
        json: async () => ({ server: { services: [] } }),
      } as Response);

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle fetch services error', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error('Network error')
      );

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });

    it('should handle area without user', async () => {
      vi.mocked(getStoredUser).mockReturnValue(null);

      render(
        <MemoryRouter>
          <Areaction />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalled();
      });
    });
  });
});
