import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../ForgotPassword';

vi.mock('../../utils/helper', () => ({
  API_BASE: 'https://test-api.com/api',
}));

describe('ForgotPassword Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  const renderPage = () => {
    return render(
      <BrowserRouter>
        <ForgotPassword />
      </BrowserRouter>
    );
  };

  describe('Rendering', () => {
    it('should render forgot password page', () => {
      renderPage();

      expect(screen.getByText('Forgot Password')).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
    });

    it('should render description text', () => {
      renderPage();

      expect(screen.getByText(/enter your email address/i)).toBeInTheDocument();
      expect(screen.getByText(/we'll send you a link/i)).toBeInTheDocument();
    });

    it('should have a back to login link', () => {
      renderPage();

      const backLink = screen.getByRole('link', { name: /back to login/i });
      expect(backLink).toHaveAttribute('href', '/login');
    });
  });

  describe('Form Interaction', () => {
    it('should allow typing in email input', () => {
      renderPage();

      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      expect(emailInput.value).toBe('test@example.com');
    });
  });

  describe('Successful Submission', () => {
    it('should show success message on successful submission', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({}),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/if that email exists/i)).toBeInTheDocument();
        expect(screen.getByText(/check your inbox/i)).toBeInTheDocument();
      });
    });

    it('should call API with correct email', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({}),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          'https://test-api.com/api/auth/password-reset/',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'user@example.com' }),
          })
        );
      });
    });

    it('should show loading state during submission', async () => {
      globalThis.fetch = vi.fn(() =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: () => Promise.resolve({}),
              } as Response),
            100
          )
        )
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      expect(screen.getByText(/sending/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      await waitFor(() => {
        expect(screen.getByText(/if that email exists/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show detail error message if error field not present', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ detail: 'Rate limit exceeded' }),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
      });
    });

    it('should show fallback error message if no specific error provided', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({}),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to request password reset/i)).toBeInTheDocument();
      });
    });

    it('should handle network error', async () => {
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
        expect(screen.getByText(/please try again later/i)).toBeInTheDocument();
      });
    });

    it('should handle JSON parse error', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.reject(new Error('Invalid JSON')),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to request password reset/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form State Management', () => {
    it('should clear previous success when re-submitting', async () => {
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({}),
        } as Response)
      );

      renderPage();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test1@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/if that email exists/i)).toBeInTheDocument();
      });

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          json: () => Promise.resolve({ error: 'Error' }),
        } as Response)
      );

      fireEvent.change(emailInput, { target: { value: 'test2@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.queryByText(/if that email exists/i)).not.toBeInTheDocument();
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      renderPage();

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });

    it('should have submit button', () => {
      renderPage();

      const submitButton = screen.getByRole('button', { name: /send reset link/i });
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('should have accessible navigation link', () => {
      renderPage();

      const backLink = screen.getByRole('link', { name: /back to login/i });
      expect(backLink).toBeInTheDocument();
    });
  });
});
