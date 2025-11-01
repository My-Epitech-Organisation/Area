import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EmailVerificationBanner from '../EmailVerificationBanner';
import { API_BASE } from '../../utils/helper';

globalThis.fetch = vi.fn();

describe('EmailVerificationBanner Component', () => {
  const mockOnVerificationSent = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering and Visibility', () => {
    it('should not render when user is null', () => {
      const { container } = render(<EmailVerificationBanner user={null} />);

      expect(container.firstChild).toBeNull();
    });

    it('should not render when email is already verified', () => {
      const user = {
        email: 'test@example.com',
        email_verified: true,
      };

      const { container } = render(<EmailVerificationBanner user={user} />);

      expect(container.firstChild).toBeNull();
    });

    it('should render when email is not verified', () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      render(<EmailVerificationBanner user={user} />);

      expect(screen.getByText(/your account is not verified yet/i)).toBeInTheDocument();
    });

    it('should render when email_verified is undefined', () => {
      const user = {
        email: 'test@example.com',
      };

      render(<EmailVerificationBanner user={user} />);

      expect(screen.getByText(/your account is not verified yet/i)).toBeInTheDocument();
    });
  });

  describe('Resend Verification Email', () => {
    it('should render resend button when email is not verified', () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      render(<EmailVerificationBanner user={user} />);

      expect(screen.getByText(/resend verification email/i)).toBeInTheDocument();
    });

    it('should show success message when verification email is sent successfully', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response);

      render(<EmailVerificationBanner user={user} onVerificationSent={mockOnVerificationSent} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/verification email sent/i)).toBeInTheDocument();
      });

      expect(mockOnVerificationSent).toHaveBeenCalledTimes(1);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        `${API_BASE}/auth/send-verification-email/`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should show error message when no token is found', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.removeItem('access');

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/please log in again/i)).toBeInTheDocument();
      });

      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should show error message when API returns error with detail', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Rate limit exceeded' }),
      } as Response);

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
      });
    });

    it('should show error message when API returns error with message', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Email service unavailable' }),
      } as Response);

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/email service unavailable/i)).toBeInTheDocument();
      });
    });

    it('should show default error message when API returns error without details', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      } as Response);

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to send verification email/i)).toBeInTheDocument();
      });
    });

    it('should show network error message when fetch throws', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockRejectedValueOnce(new Error('Network error'));

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('should disable button while request is in progress', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      let resolvePromise: (value: Response) => void;
      const promise = new Promise<Response>((resolve) => {
        resolvePromise = resolve;
      });

      vi.mocked(globalThis.fetch).mockReturnValueOnce(promise);

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });

      expect(resendButton).not.toBeDisabled();

      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(resendButton).toBeDisabled();
      });

      resolvePromise!({
        ok: true,
        json: async () => ({}),
      } as Response);

      await waitFor(() => {
        expect(resendButton).not.toBeDisabled();
      });
    });

    it('should not call onVerificationSent if callback not provided', async () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      localStorage.setItem('access', 'test-token');

      vi.mocked(globalThis.fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      } as Response);

      render(<EmailVerificationBanner user={user} />);

      const resendButton = screen.getByRole('button', { name: /resend|verification/i });
      fireEvent.click(resendButton);

      await waitFor(() => {
        expect(screen.getByText(/verification email sent/i)).toBeInTheDocument();
      });

      expect(globalThis.fetch).toHaveBeenCalled();
    });
  });

  describe('Styling and Structure', () => {
    it('should have proper container styling', () => {
      const user = {
        email: 'test@example.com',
        email_verified: false,
      };

      const { container } = render(<EmailVerificationBanner user={user} />);

      const banner = container.firstChild as HTMLElement;
      expect(banner).toHaveClass('mb-6');
      expect(banner).toHaveClass('rounded-lg');
    });

    it('should display user email in the banner', () => {
      const user = {
        email: 'john.doe@example.com',
        email_verified: false,
      };

      render(<EmailVerificationBanner user={user} />);

      expect(screen.getByText(/john\.doe@example\.com/i)).toBeInTheDocument();
    });
  });
});
