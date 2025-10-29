import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import OAuthCallback from '../OAuthCallback';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('OAuthCallback Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('Success Scenarios', () => {
    it('should show success message when OAuth connection succeeds', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?success=true&service=GitHub&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /success/i })).toBeInTheDocument();
      expect(screen.getByText(/successfully connected to github/i)).toBeInTheDocument();
      expect(screen.getByText(/redirecting to services/i)).toBeInTheDocument();
    });

    it('should show reconnected message when OAuth updates existing connection', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/google?success=true&service=Google&created=false']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /success/i })).toBeInTheDocument();
      expect(screen.getByText(/successfully reconnected to google/i)).toBeInTheDocument();
    });

    it('should redirect to services page after 2 seconds on success', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?success=true&service=GitHub&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(mockNavigate).not.toHaveBeenCalled();

      vi.advanceTimersByTime(2000);

      expect(mockNavigate).toHaveBeenCalledWith('/services');
    });

    it('should display success icon on successful connection', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?success=true&service=GitHub&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /success/i })).toBeInTheDocument();
      const successElement = screen.getByText(/successfully connected/i);
      expect(successElement).toHaveClass('text-green-300');
    });
  });

  describe('Error Scenarios', () => {
    it('should show error message when OAuth fails with error parameter', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=access_denied&message=User%20denied%20access']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      expect(screen.getByText(/user denied access/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /back to services/i })).toBeInTheDocument();
    });

    it('should show default error message when no message provided', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=invalid_token']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      expect(screen.getByText(/authentication failed: invalid_token/i)).toBeInTheDocument();
    });

    it('should redirect to services after 3 seconds on error', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=access_denied']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(mockNavigate).not.toHaveBeenCalled();

      vi.advanceTimersByTime(3000);

      expect(mockNavigate).toHaveBeenCalledWith('/services');
    });

    it('should handle missing required parameters', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      expect(screen.getByText(/invalid oauth callback.*missing required parameters/i)).toBeInTheDocument();
    });

    it('should handle unexpected authentication state', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?service=GitHub']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
      expect(screen.getByText(/unexpected authentication state/i)).toBeInTheDocument();
    });

    it('should allow manual navigation back to services on error', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=access_denied']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      const backButton = screen.getByRole('button', { name: /back to services/i });
      backButton.click();

      expect(mockNavigate).toHaveBeenCalledWith('/services');
    });
  });

  describe('Processing State', () => {
    it('should render component without crashing', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?success=true&service=GitHub&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByRole('heading', { name: /success/i })).toBeInTheDocument();
    });
  });

  describe('Different OAuth Providers', () => {
    it('should handle GitHub OAuth callback', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?success=true&service=GitHub&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/github/i)).toBeInTheDocument();
    });

    it('should handle Google OAuth callback', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/google?success=true&service=Google&created=true']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/google/i)).toBeInTheDocument();
    });

    it('should handle Gmail OAuth callback', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/gmail?success=true&service=Gmail&created=false']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/gmail/i)).toBeInTheDocument();
      expect(screen.getByText(/reconnected/i)).toBeInTheDocument();
    });
  });

  describe('URL Encoding', () => {
    it('should decode URL-encoded error messages', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=invalid&message=Invalid%20OAuth%20state%20parameter']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/invalid oauth state parameter/i)).toBeInTheDocument();
    });

    it('should handle special characters in error messages', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=error&message=Connection%20timeout%20%3A%20retry%20later']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      expect(screen.getByText(/connection timeout : retry later/i)).toBeInTheDocument();
    });
  });

  describe('UI Elements', () => {
    it('should display error icon on failure', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=access_denied']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      const errorText = screen.getByText(/connection failed/i);
      expect(errorText).toBeInTheDocument();

      const errorMessage = screen.getByText(/authentication failed/i);
      expect(errorMessage).toHaveClass('text-red-300');
    });

    it('should have accessible back button on error', () => {
      render(
        <MemoryRouter initialEntries={['/oauth/callback/github?error=access_denied']}>
          <OAuthCallback />
        </MemoryRouter>
      );

      const backButton = screen.getByRole('button', { name: /back to services/i });
      expect(backButton).toBeInTheDocument();
      expect(backButton).toHaveClass('bg-indigo-600');
    });
  });
});
