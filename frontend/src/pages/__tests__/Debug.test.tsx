import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Debug from '../Debug';
import * as debugApi from '../../services/debugApi';

vi.mock('../../services/debugApi', () => ({
  triggerDebugAction: vi.fn(),
  getDebugExecutions: vi.fn(),
}));

describe('Debug Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
    localStorage.setItem('access', 'test-token');
  });

  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  describe('Loading State', () => {
    it('should show loading state initially', () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockImplementation(
        () =>
          new Promise(() => {
          })
      );

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      expect(screen.getByText(/loading debug console/i)).toBeInTheDocument();
    });
  });

  describe('No Debug Areas', () => {
    it('should show empty state when no debug areas exist', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/no debug areas found/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/debug_manual_trigger/i)).toBeInTheDocument();
      expect(screen.getByText(/create debug area/i)).toBeInTheDocument();
    });

    it('should have link to create debug area', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: [] }),
        });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/create debug area/i)).toBeInTheDocument();
      });

      const link = screen.getByText(/create debug area/i).closest('a');
      expect(link).toHaveAttribute('href', '/Areaction');
    });
  });

  describe('With Debug Areas', () => {
    const mockDebugAreas = [
      { id: 1, name: 'Test Debug Area 1', status: 'active', action: 5 },
      { id: 2, name: 'Test Debug Area 2', status: 'inactive', action: 5 },
    ];

    const mockActions = [
      { id: 5, name: 'debug_manual_trigger', service: 'system' },
      { id: 6, name: 'other_action', service: 'github' },
    ];

    beforeEach(() => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockDebugAreas }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockActions }),
        });

      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area 1',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: [],
      });
    });

    it('should render debug console with areas', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Debug Console')).toBeInTheDocument();
      });

      expect(screen.getByText(/manually trigger actions/i)).toBeInTheDocument();
      expect(screen.getByText('Debug Actions')).toBeInTheDocument();
      expect(screen.getByText('Execution Log')).toBeInTheDocument();
    });

    it('should display debug areas', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area 1')).toBeInTheDocument();
      });

      expect(screen.getByText('Test Debug Area 2')).toBeInTheDocument();
      expect(screen.getAllByText('active')).toHaveLength(1);
      expect(screen.getByText('inactive')).toBeInTheDocument();
    });

    it('should show trigger buttons for each area', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area 1')).toBeInTheDocument();
      });

      const triggerButtons = screen.getAllByText(/⚡ trigger now/i);
      expect(triggerButtons).toHaveLength(2);
    });

    it('should disable trigger button for inactive areas', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area 2')).toBeInTheDocument();
      });

      const buttons = screen.getAllByText(/⚡ trigger now/i);
      const inactiveAreaButton = buttons[1];
      expect(inactiveAreaButton).toBeDisabled();
    });
  });

  describe('Triggering Actions', () => {
    const mockDebugAreas = [
      { id: 1, name: 'Test Debug Area', status: 'active', action: 5 },
    ];

    const mockActions = [
      { id: 5, name: 'debug_manual_trigger', service: 'system' },
    ];

    beforeEach(() => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockDebugAreas }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockActions }),
        });

      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: [],
      });
    });

    it('should trigger action when button clicked', async () => {
      (debugApi.triggerDebugAction as ReturnType<typeof vi.fn>).mockResolvedValue({
        message: 'Action triggered successfully',
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area')).toBeInTheDocument();
      });

      const triggerButton = screen.getByText(/⚡ trigger now/i);
      fireEvent.click(triggerButton);

      await waitFor(() => {
        expect(debugApi.triggerDebugAction).toHaveBeenCalledWith(1);
      });
    });

    it('should show success message after triggering', async () => {
      (debugApi.triggerDebugAction as ReturnType<typeof vi.fn>).mockResolvedValue({
        message: 'Action triggered successfully',
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area')).toBeInTheDocument();
      });

      const triggerButton = screen.getByText(/⚡ trigger now/i);
      fireEvent.click(triggerButton);

      await waitFor(() => {
        expect(screen.getByText(/action triggered successfully/i)).toBeInTheDocument();
      });
    });

    it('should show error message on trigger failure', async () => {
      (debugApi.triggerDebugAction as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error('Failed to trigger action')
      );

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area')).toBeInTheDocument();
      });

      const triggerButton = screen.getByText(/⚡ trigger now/i);
      fireEvent.click(triggerButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to trigger action/i)).toBeInTheDocument();
      });
    });
  });

  describe('Execution Log', () => {
    const mockDebugAreas = [
      { id: 1, name: 'Test Debug Area', status: 'active', action: 5 },
    ];

    const mockActions = [
      { id: 5, name: 'debug_manual_trigger', service: 'system' },
    ];

    beforeEach(() => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockDebugAreas }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockActions }),
        });
    });

    it('should show empty execution log initially', async () => {
      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: [],
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/no executions yet/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/trigger an action to see execution logs/i)).toBeInTheDocument();
    });

    it('should display execution details', async () => {
      const mockExecutions = [
        {
          id: 1,
          status: 'success',
          created_at: '2025-10-29T18:00:00Z',
          completed_at: '2025-10-29T18:00:05Z',
          reaction_result: { status: 'sent', recipient: 'test@example.com' },
          error_message: null,
        },
      ];

      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: mockExecutions,
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('SUCCESS')).toBeInTheDocument();
      });

      expect(screen.getByText(/reaction result/i)).toBeInTheDocument();
    });

    it('should display error message in execution log', async () => {
      const mockExecutions = [
        {
          id: 1,
          status: 'failed',
          created_at: '2025-10-29T18:00:00Z',
          completed_at: null,
          reaction_result: null,
          error_message: 'Connection timeout',
        },
      ];

      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: mockExecutions,
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('FAILED')).toBeInTheDocument();
      });

      expect(screen.getByText(/connection timeout/i)).toBeInTheDocument();
    });

    it('should show area details in execution log header', async () => {
      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Test Debug Area',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: [],
      });

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Debug Area')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors gracefully', async () => {
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Network error')
      );

      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText(/loading debug console/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Area Selection', () => {
    const mockDebugAreas = [
      { id: 1, name: 'Debug Area 1', status: 'active', action: 5 },
      { id: 2, name: 'Debug Area 2', status: 'active', action: 5 },
    ];

    const mockActions = [
      { id: 5, name: 'debug_manual_trigger', service: 'system' },
    ];

    beforeEach(() => {
      (globalThis.fetch as ReturnType<typeof vi.fn>)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockDebugAreas }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ results: mockActions }),
        });

      (debugApi.getDebugExecutions as ReturnType<typeof vi.fn>).mockResolvedValue({
        area_name: 'Debug Area 1',
        action: 'debug_manual_trigger',
        reaction: 'send_email',
        executions: [],
      });
    });

    it('should highlight selected area', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Debug Area 1')).toBeInTheDocument();
      });

      expect(screen.getByText('Debug Area 2')).toBeInTheDocument();
    });

    it('should allow clicking to select different area', async () => {
      render(
        <BrowserRouter>
          <Debug />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Debug Area 2')).toBeInTheDocument();
      });

      const secondArea = screen.getByText('Debug Area 2').closest('div');
      fireEvent.click(secondArea!);

      await waitFor(() => {
        expect(debugApi.getDebugExecutions).toHaveBeenCalledWith(2);
      });
    });
  });
});
